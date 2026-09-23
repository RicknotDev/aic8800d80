# Linux 6.12 compatibility fix

This fork contains a compatibility fix for the AIC8800D80 Linux driver on Linux 6.12 kernels, including Debian 13.

## What was fixed

The original driver used:

```c
KERNEL_VERSION(6, 13, 0)
```

for kernel API changes that are already required on Linux 6.12.

The affected code was updated to use:

```c
KERNEL_VERSION(6, 12, 0)
```

This was applied to the Wi-Fi driver and Bluetooth loader, including:

- `drivers/aic8800/aic8800_fdrv/aic_priv_cmd.c`
- `drivers/aic8800/aic8800_fdrv/aic_priv_cmd.h`
- `drivers/aic8800/aic8800_fdrv/rwnx_main.c`
- `drivers/aic8800/aic8800_fdrv/rwnx_main.h`
- `drivers/aic8800/aic_load_fw/aic_bluetooth_main.c`

## Tested environment

- OS: Debian GNU/Linux 13 (trixie)
- Kernel: `6.12.107+deb13-amd64`
- Device: Tenda U11 (AIC8800D80)

The goal of this fork is to make the existing AIC8800D80 driver build correctly on Linux 6.12 without changing its behavior for older supported kernels.
