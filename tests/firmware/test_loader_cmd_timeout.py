#!/usr/bin/env python3
"""Exercise the loader's real cmd_mgr_queue() wait paths with mocked kernel services."""
from pathlib import Path
import os
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
LOADER = ROOT / "drivers/aic8800/aic_load_fw"

PRELUDE = r"""
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#define BIT(n) (1U << (n))
#define KERN_CRIT ""
#define printk printf
#define RWNX_80211_CMD_TIMEOUT_MS 2000
#define EINTR 4
#define ENOMEM 12
#define ENODEV 19
#define EPIPE 32
#define ETIMEDOUT 110
#define ERESTARTSYS 512
#define lockdep_assert_held(lock) ((void)(lock))

struct list_head { struct list_head *next, *prev; };
struct completion { int done; };
struct lmac_msg { int id; unsigned int param_len; unsigned int param[1]; };
struct rwnx_cmd {
    struct list_head list;
    int tkn, id, reqid, result;
    unsigned int flags;
    struct lmac_msg *a2e_msg;
    void *e2a_msg;
    struct completion complete;
};
enum { RWNX_CMD_MGR_STATE_INITED, RWNX_CMD_MGR_STATE_CRASHED };
struct rwnx_cmd_mgr {
    int state, queue_sz, max_queue_sz, next_tkn, lock;
    struct list_head cmds;
    void *usbdev;
    int (*queue)(struct rwnx_cmd_mgr *, struct rwnx_cmd *);
};
typedef unsigned short lmac_msg_id_t;
enum { BUS_DOWN_ST, BUS_UP_ST };
struct aicwf_bus { int state; };
struct aic_usb_dev { struct aicwf_bus *bus_if; struct rwnx_cmd_mgr cmd_mgr; };
#define GFP_ATOMIC 0
#define GFP_KERNEL 0
#define container_of(ptr, type, member) ((type *)((char *)(ptr) - __builtin_offsetof(type, member)))

static struct rwnx_cmd cmd;
static struct lmac_msg msg;
static struct rwnx_cmd_mgr mgr;
static long wait_result;
static bool cfm_during_wait;
static int cmd_frees, msg_frees, queued;
static bool alloc_fails;

#define spin_lock_bh(lock) ((void)(lock))
#define spin_unlock_bh(lock) ((void)(lock))
#define init_completion(c) ((c)->done = 0)
#define complete(c) ((c)->done = 1)
#define msecs_to_jiffies(ms) ((unsigned long)(ms))
#define list_entry(ptr, type, member) ((type *)(ptr))

static int list_empty(const struct list_head *head) { return head->next == head; }
static void list_add_tail(struct list_head *item, struct list_head *head)
{
    item->prev = head->prev;
    item->next = head;
    head->prev->next = item;
    head->prev = item;
}
static void list_del(struct list_head *item)
{
    item->prev->next = item->next;
    item->next->prev = item->prev;
}
static void kfree(const void *ptr)
{
    if (ptr == &cmd)
        cmd_frees++;
    else if (ptr == &msg)
        msg_frees++;
    else
        abort();
}
static void *kzalloc(unsigned long size, int flags)
{
    (void)size; (void)flags;
    return alloc_fails ? NULL : &cmd;
}
static void aicwf_set_cmd_tx(void *dev, struct lmac_msg *m, unsigned int len)
{
    (void)dev; (void)m; (void)len;
}
"""

MOCK_WAIT = r"""
static void cmd_complete(struct rwnx_cmd_mgr *cmd_mgr, struct rwnx_cmd *cmd);
static long wait_for_completion_killable_timeout(struct completion *c, unsigned long tout)
{
    (void)c; (void)tout;
    if (cfm_during_wait) {
        /* What cmd_mgr_msgind() does for a matching confirmation. */
        cmd.flags &= ~RWNX_CMD_FLAG_WAIT_CFM;
        cmd_complete(&mgr, &cmd);
    }
    return wait_result;
}
"""

CHECKS = r"""
#define CHECK(expr) do { if (!(expr)) { printf("failed: %s\n", #expr); exit(1); } } while (0)

static int run(long result, bool cfm)
{
    mgr = (struct rwnx_cmd_mgr){ .state = RWNX_CMD_MGR_STATE_INITED, .max_queue_sz = 8 };
    mgr.cmds.next = mgr.cmds.prev = &mgr.cmds;
    cmd = (struct rwnx_cmd){ .flags = RWNX_CMD_FLAG_REQ_CFM, .a2e_msg = &msg };
    wait_result = result;
    cfm_during_wait = cfm;
    cmd_frees = msg_frees = 0;
    return cmd_mgr_queue(&mgr, &cmd);
}

static void check_released(void)
{
    CHECK(list_empty(&mgr.cmds));
    CHECK(mgr.queue_sz == 0);
    CHECK(cmd_frees == 1);
    CHECK(msg_frees == 1);
}

static int count_queue(struct rwnx_cmd_mgr *m, struct rwnx_cmd *c)
{
    (void)m; (void)c;
    queued++;
    return 0;
}

static int send(int bus_state, bool no_memory)
{
    struct aicwf_bus bus = { .state = bus_state };
    struct aic_usb_dev dev = { .bus_if = &bus, .cmd_mgr.queue = count_queue };
    unsigned int cfm = 0;

    alloc_fails = no_memory;
    cmd_frees = msg_frees = queued = 0;
    return rwnx_send_msg(&dev, msg.param, 1, 0, &cfm);
}

int main(void)
{
    /* Nothing was sent, so the caller must not read the unfilled cfm. */
    CHECK(send(BUS_DOWN_ST, false) == -ENODEV);
    CHECK(queued == 0 && msg_frees == 1 && cmd_frees == 0);
    CHECK(send(BUS_UP_ST, true) == -ENOMEM);
    CHECK(queued == 0 && msg_frees == 1 && cmd_frees == 0);
    CHECK(send(BUS_UP_ST, false) == 0);
    CHECK(queued == 1);

    /* A confirmation in time: success. */
    CHECK(run(1, true) == 0);
    CHECK(mgr.state == RWNX_CMD_MGR_STATE_INITED);
    check_released();

    /* No confirmation: the caller must not read the unfilled cfm. */
    CHECK(run(0, false) == -ETIMEDOUT);
    CHECK(mgr.state == RWNX_CMD_MGR_STATE_CRASHED);
    check_released();

    /* A fatal signal: same, and the command must not stay queued. */
    CHECK(run(-ERESTARTSYS, false) == -ERESTARTSYS);
    CHECK(mgr.state == RWNX_CMD_MGR_STATE_CRASHED);
    check_released();

    /* The confirmation arrives as the wait ends: the cfm is valid. */
    CHECK(run(0, true) == 0);
    CHECK(mgr.state == RWNX_CMD_MGR_STATE_INITED);
    check_released();
    return 0;
}
"""


def function(source, signature):
    start = source.index(signature)
    brace = source.index("{", start)
    end, depth = brace + 1, 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]


class LoaderCommandTimeoutTests(unittest.TestCase):
    def test_send_and_wait_paths(self):
        source = (LOADER / "aicbluetooth_cmds.c").read_text(errors="replace")
        header = (LOADER / "aicbluetooth_cmds.h").read_text(errors="replace")
        defines = re.findall(r"(?m)^#define RWNX_CMD_FLAG_\w+.*$", header)
        defines += re.findall(r"(?m)^#define RWNX_CMD_WAIT_COMPLETE\(flags\) \\\n.*$", header)
        self.assertGreater(len(defines), 1)
        code = PRELUDE + "\n".join(defines) + MOCK_WAIT
        for signature in ("static void cmd_dump(", "static void cmd_complete(",
                          "static int cmd_mgr_queue(", "static void rwnx_msg_free(",
                          "static int rwnx_send_msg("):
            code += function(source, signature) + "\n"
        code += CHECKS
        with tempfile.TemporaryDirectory(prefix="aic-cmd-timeout-") as temp:
            c_file, binary = Path(temp) / "test.c", Path(temp) / "test"
            c_file.write_text(code)
            subprocess.run([os.environ.get("CC", "cc"), "-std=gnu11", "-o", str(binary),
                            str(c_file)], check=True)
            subprocess.run([str(binary)], check=True)


if __name__ == "__main__":
    unittest.main()
