#!/usr/bin/env bash
# Download a kernel release and prepare it for external module builds.
# Usage: ci/prepare-kernel.sh VERSION|mainline DEST_DIR
set -euo pipefail

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 VERSION|mainline DEST_DIR" >&2
    exit 2
fi

version=$1
dest=$2
download_dir=$(mktemp -d)
trap 'rm -rf "$download_dir"' EXIT

if [ "$version" = mainline ]; then
    # Release candidates come from git.kernel.org, which has no sha256sums file.
    url=$(curl -fsSL --retry 3 https://www.kernel.org/releases.json | python3 -c '
import json, sys
print(next(r["source"] for r in json.load(sys.stdin)["releases"] if r["moniker"] == "mainline"))')
    archive="$download_dir/${url##*/}"
    curl -fsSL --retry 3 -o "$archive" "$url"
else
    base="https://cdn.kernel.org/pub/linux/kernel/v${version%%.*}.x"
    name="linux-$version.tar.xz"
    archive="$download_dir/$name"
    curl -fsSL --retry 3 -o "$archive" "$base/$name"
    curl -fsSL --retry 3 -o "$download_dir/sha256sums.asc" "$base/sha256sums.asc"
    (cd "$download_dir" && grep -E "  $name\$" sha256sums.asc | sha256sum --check --strict -)
fi

mkdir -p "$dest"
tar -xf "$archive" -C "$dest" --strip-components=1

make -C "$dest" x86_64_defconfig
"$dest/scripts/config" --file "$dest/.config" \
    --enable WIRELESS \
    --enable USB_SUPPORT \
    --enable USB \
    --enable KPROBES \
    --module CFG80211 \
    --disable WERROR
make -C "$dest" olddefconfig

for option in CONFIG_CFG80211=m CONFIG_USB=y CONFIG_KPROBES=y; do
    grep -qx "$option" "$dest/.config" || {
        echo "Kernel config is missing $option" >&2
        exit 1
    }
done

make -C "$dest" -j"$(nproc)" modules_prepare
