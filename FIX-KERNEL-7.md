# AIC8800D80 Driver Fix for Linux Kernel 7.x

## Problem

This driver fails to compile on Linux kernel >= 6.14 (including Kali's 7.1.5+kali-amd64)
due to two upstream kernel API changes:

### 1. cfg80211 callbacks: `struct net_device *` → `struct wireless_dev *`

Since kernel 6.14, cfg80211 ops use `struct wireless_dev *` as the second parameter
(instead of `struct net_device *`) for the following callbacks:

- `add_key` / `get_key` / `del_key` / `set_default_mgmt_key`
- `add_station` / `del_station` / `change_station`
- `get_station` / `dump_station`

In this driver only some callbacks had been migrated (e.g. `mgmt_tx`, `add_iface`),
leaving the station/key callbacks with the old signature, which breaks the build:

```
error: initialization of ... from incompatible pointer type [-Wincompatible-pointer-types]
error: passing argument 1 of 'cfg80211_new_sta' from incompatible pointer type
```

### 2. `ieee80211_mgmt` struct: removed `.u` union member in TDLS action

In newer kernels the anonymous union inside `u.action` was flattened and
`action_code` moved to the outer `u.action` level:

```
mgmt->u.action.u.tdls_discover_resp.action_code  →  mgmt->u.action.action_code
mgmt->u.action.u.tdls_discover_resp.dialog_token →  mgmt->u.action.tdls_discover_resp.dialog_token
```

## Changes

| File | Description |
|------|-------------|
| `drivers/aic8800/aic8800_fdrv/rwnx_main.c` | Adapt 9 cfg80211 callbacks to `wireless_dev *`, update 5 call sites (`cfg80211_new_sta`, `cfg80211_del_sta`, `rwnx_cfg80211_add_key`, `rwnx_cfg80211_del_station_compat`) |
| `drivers/aic8800/aic8800_fdrv/rwnx_tdls.c` | Adapt `ieee80211_mgmt` TDLS discover response access (remove `.u`, move `action_code`) |

Inside the migrated callbacks, the original `net_device *` is obtained with
`struct net_device *dev = wdev->netdev;` so the rest of the function body is unchanged.

## Tested

- **Kernel**: 7.1.5+kali-amd64 (Kali GNU/Linux Rolling 2026.3)
- **Build**: `make` — success (both `aic8800_fdrv.ko` and `aic_load_fw.ko`)
- **DKMS**: `aic8800/1.0.0, 7.1.5+kali-amd64, x86_64: installed`
- **Module load**: `modprobe aic8800_fdrv` / `aic_load_fw` — loaded without errors
- **Hardware**: AIC 8800D80 (USB ID `368b:8d81`)

## How to use

```bash
git clone https://github.com/<your-fork>/aic8800d80.git
cd aic8800d80
sudo ./install.sh --force --skip-deps
```

> Note: `--skip-deps` skips `mokutil` installation (required only for Secure Boot
> detection, and its .deb may fail to download from Cloudflare-fronted mirrors
> when not using a proxy).

## Troubleshooting

### USB device stuck in `resuming` state (Hyper-V / virtualized USB)

If `modprobe` hangs and `dmesg` shows a task stuck in `usb_port_resume` →
`usb_control_msg`, USB autosuspend is likely breaking the device wakeup.
Disable it by adding `usbcore.autosuspend=-1` to the kernel cmdline
(`GRUB_CMDLINE_LINUX_DEFAULT` in `/etc/default/grub`, then `sudo update-grub`).

Also note: some Hyper-V guest configs do not expose a virtual USB controller at all,
so a USB WiFi dongle plugged into the host will not appear inside the guest.