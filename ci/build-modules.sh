#!/usr/bin/env bash
# Build all driver modules against a kernel tree from ci/prepare-kernel.sh.
# Usage: ci/build-modules.sh KERNEL_DIR
set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 KERNEL_DIR" >&2
    exit 2
fi

kernel_dir=$(realpath "$1")
repo_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
module_dir="$repo_dir/drivers/aic8800"

# modules_prepare produces no vmlinux or Module.symvers, so modpost cannot
# resolve kernel symbols. Compile errors still fail the build.
make -C "$kernel_dir" M="$module_dir" KBUILD_MODPOST_WARN=1 -j"$(nproc)" modules

for module in aic_load_fw/aic_load_fw.ko aic8800_fdrv/aic8800_fdrv.ko \
    aic_zlp_quirk/aic_zlp_quirk.ko; do
    test -s "$module_dir/$module" || {
        echo "Missing module: $module" >&2
        exit 1
    }
done

echo "All three modules built against $(make -s -C "$kernel_dir" kernelversion)"
