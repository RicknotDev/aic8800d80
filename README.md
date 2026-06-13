# 🛜 AIC8800D80 Linux Driver

[![License: GPL v2](https://img.shields.io/badge/License-GPLv2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Kernel Support](https://img.shields.io/badge/Kernel-6.x-green.svg)](https://kernel.org/)
[![Distros Supported](https://img.shields.io/badge/Distros-8-blueviolet.svg)](#-compatibility--distros-and-package-managers)
[![Language](https://img.shields.io/badge/Language-C-00599C.svg)](https://en.wikipedia.org/wiki/C_(programming_language))
[![Maintained](https://img.shields.io/badge/Maintained%20by-RicknotDev-brightgreen)](https://github.com/RicknotDev)

Universal Linux driver for AIC8800D80 Wi-Fi chipsets with DKMS and multi-distro support.

---

## 📋 Description

This project provides a **complete kernel driver** for Wi-Fi devices based on the **AIC8800D80 chipset**, compatible with cards like Tenda U11 and AX913B. The driver includes:

- **Automatic installation** via DKMS to maintain compatibility after kernel updates
- **Multi-platform support** for 8 major Linux distributions
- **Embedded firmware** with configurations for multiple chipset variants
- **Automatic udev rules** for better system integration

### Why use this driver?

- ✅ Compatible with kernels **6.x** (7.x with `--force`)
- ✅ **Automatic installation** on Debian, Fedora, Arch, Alpine, and more
- ✅ **No hidden dependencies** — automatically detects what you need
- ✅ Support for **Vendor ID 368B** (Pandora clones)
- ✅ **Integrated DKMS** — automatically reinstalls after kernel updates

---

## ⚡ Key Features

- 🔧 **Automatic installation with DKMS** — recompiles after kernel updates
- 📦 **Pre-packaged firmware** for D80, D80N, D80X2, DC, DLN variants
- 🐧 **8 distributions supported** — Debian, Fedora, Arch, Alpine, Void, Solus, openSUSE, CentOS
- 🛡️ **Secure Boot detection** — warns if it may affect module loading
- 🔌 **Integrated udev rules** — support for automatic USB mode switching
- 📊 **Detailed logs** — installation with clear diagnostic messages
- ⏭️ **Kernel compatibility** — automatic version checking before install

---

## 📊 Compatibility — Distros and Package Managers

| Distribution         | Package Manager | Status     | Notes                          |
|----------------------|-----------------|------------|--------------------------------|
| Debian / Ubuntu      | apt             | ✅ Stable  | Tested on Ubuntu 25.04, Debian 12 |
| Fedora / RHEL        | dnf             | ✅ Stable  | RHEL 8+ compatible             |
| CentOS / RHEL legacy | yum             | ✅ Stable  | Requires EPEL enabled          |
| Arch Linux           | pacman          | ✅ Stable  | Includes linux-headers         |
| openSUSE             | zypper          | ✅ Stable  | Leap and Tumbleweed           |
| Alpine Linux         | apk             | ✅ Stable  | Requires edge repository       |
| Void Linux           | xbps-install    | ✅ Stable  | Compilation from source        |
| Solus                | eopkg           | ✅ Stable  | Experimental support           |

### ℹ️ Unsupported distributions

If your distro is not listed, you can install the dependencies manually and then run:

```bash
sudo ./install.sh --skip-deps
```

### Distribution-specific notes

- **Alpine Linux**: Requires updating repository with `edge`
- **Void Linux / Solus**: Compiler may take longer on first run
- All distros require `sudo` access or root permission

---

## 📋 Prerequisites

### Required software

| Component       | Minimum Version | Purpose                              |
|-----------------|-----------------|--------------------------------------|
| Linux Kernel    | 6.0.0           | Base operating system                |
| DKMS            | 3.0             | Dynamic Kernel Module Support        |
| Compiler (gcc)  | 9.x             | Build tools                          |
| Make            | 4.0             | Build system                         |
| Linux Headers   | Kernel-matched  | Kernel development files             |

### Optional tools

- `mokutil` — for Secure Boot management
- `udevadm` — for reloading udev rules (usually included)

### Disk space

- **Minimum**: 500 MB (driver + firmware)
- **Recommended**: 2 GB (compilation space)

---

## 🚀 Installation

### Method 1: Automatic Installation (Recommended)

The fastest way for most users:

```bash
# 1. Clone the repository
git clone https://github.com/RicknotDev/aic8800d80.git
cd aic8800d80

# 2. Make installer executable
chmod +x install.sh

# 3. Run installation
sudo ./install.sh
```

The script will detect your distro, install necessary dependencies, and configure DKMS automatically.

#### Advanced installer options

```bash
# For kernel 7.x (not guaranteed, use at your own risk)
sudo ./install.sh --force

# If you already installed dependencies manually
sudo ./install.sh --skip-deps

# View full help
sudo ./install.sh --help
```

### Method 2: Manual Installation

For advanced users or unsupported distributions:

#### 2.1. Install dependencies

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y dkms build-essential linux-headers-$(uname -r)

# Fedora/RHEL
sudo dnf install -y dkms make gcc kernel-devel kernel-headers

# Arch
sudo pacman -S dkms base-devel linux-headers

# Alpine
sudo apk update && sudo apk add dkms build-base linux-headers
```

#### 2.2. Copy firmware

```bash
# Clean old firmware (IMPORTANT)
sudo rm -rf /lib/firmware/aic8800*

# Copy new firmware
sudo cp -r ./fw/aic8800D80 /lib/firmware/
```

#### 2.3. Copy udev rules

```bash
sudo cp aic.rules /usr/lib/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

#### 2.4. Compile and install with DKMS

```bash
# Navigate to driver directory
cd drivers/aic8800

# Compile
make

# Install
sudo make install

# (Optional) Generate DKMS config if not present
sudo dkms add -m aic8800 -v 1.0.0
sudo dkms build -m aic8800 -v 1.0.0
sudo dkms install -m aic8800 -v 1.0.0
```

---

## 💻 Usage / Quickstart

### Load the driver

```bash
# Load module manually
sudo modprobe aic8800_fdrv
```

The driver will load automatically on boot after installation.

### Verify it's working

```bash
# Verify module is loaded
lsmod | grep aic

# You should see something like:
# aic8800_fdrv    536576  0
# cfg80211       1146880  1 aic8800_fdrv
# aic_load_fw     69632  1 aic8800_fdrv
```

### Search and connect to Wi-Fi networks

```bash
# List available network interfaces
iwconfig

# Using NetworkManager (GNOME/KDE)
nmcli device
nmcli connection up <SSID>

# Using iwd (more modern alternative)
iwctl station wlan0 connect <SSID>
```

### Troubleshoot issues

```bash
# View kernel logs in real-time
sudo dmesg -w | grep aic

# Check detailed driver status
cat /sys/class/net/wlan0/phy80211/name

# Check if device is in download/load mode
lsusb | grep aic
```

---

## ⚙️ Configuration

### Driver parameters

The driver loads configuration files from the `fw/` folder:

```
fw/
├── aic8800D80/          # Standard variant
│   ├── aic_userconfig_8800d80.txt
│   ├── aic_powerlimit_8800d80.txt
│   └── (other firmware files)
├── aic8800D80N/         # N variant
├── aic8800D80X2/        # X2 variant
├── aic8800DC/           # DC variant
└── aic8800DLN/          # DLN variant
```

To use a specific configuration, edit the appropriate `aic_userconfig_*.txt` file before installing.

### Kernel module variables

After installation, you can adjust parameters when loading the module:

```bash
# Example: load with custom firmware path
sudo modprobe aic8800_fdrv aic_fw_path=/custom/fw/path

# View all available parameters
modinfo aic8800_fdrv
```

### Uninstall the driver

```bash
# If installed with DKMS
sudo dkms remove aic8800/1.0.0 --all
sudo rm -rf /lib/firmware/aic8800*
sudo rm /usr/lib/udev/rules.d/aic.rules
sudo udevadm control --reload-rules

# If installed manually
cd drivers/aic8800
sudo make uninstall
```

---

## 📁 Project Structure

```
aic8800d80/
├── install.sh                    # Universal automatic installer
├── diagnostic_build.sh           # Diagnostic script
├── dkms.conf                     # DKMS configuration
├── README.md                     # This file
├── drivers/
│   └── aic8800/
│       ├── Makefile              # Main build script
│       ├── aic_load_fw/          # Firmware loader module
│       │   ├── aic_bluetooth_main.c
│       │   ├── aicwf_usb.c
│       │   └── (+ compatibility files)
│       └── aic8800_fdrv/         # Wi-Fi driver module
│           ├── rwnx_main.c       # Entry point
│           ├── rwnx_tx.c         # Transmission
│           ├── rwnx_rx.c         # Reception
│           └── (+ support files)
├── fw/                           # Binary firmware
│   ├── aic8800D80/
│   ├── aic8800D80N/
│   ├── aic8800D80X2/
│   ├── aic8800DC/
│   └── aic8800DLN/
├── aic.rules                     # udev rules
├── usb_modeswitch/              # USB mode switching config
└── bazzite/                      # Bazzite packaging (rpm-ostree)
```

### Main modules

- **aic_load_fw**: Loads firmware to USB device and manages Bluetooth
- **aic8800_fdrv**: Main Wi-Fi driver that interacts with cfg80211 and mac80211

---

## 🧪 Tests and Diagnostics

### Run full diagnostic

```bash
# Script checks structure, DKMS, firmware, and kernel
chmod +x diagnostic_build.sh
sudo ./diagnostic_build.sh
```

This script validates:
- ✅ Presence of build files
- ✅ DKMS configuration
- ✅ Firmware installed correctly
- ✅ Kernel and tool compatibility
- ✅ Build logs (if present)

### Test manual compilation

```bash
cd drivers/aic8800
make clean
make VERBOSE=1  # Show compilation details
```

---

## 🤝 Contribution

Contributions are welcome. To contribute:

### 1. Fork the project

```bash
git clone https://github.com/RicknotDev/aic8800d80.git
cd aic8800d80
```

### 2. Create a branch for your feature

```bash
git checkout -b feature/my-improvement
```

### 3. Make commits with clear messages

```bash
git commit -m "feat: add kernel 7.x support"
git commit -m "fix: resolve Alpine loading issue"
```

### 4. Push changes and create a Pull Request

```bash
git push origin feature/my-improvement
```

Then open a PR on GitHub describing:
- What problem it solves
- How it was tested
- Any behavior changes

### Code conventions

- Use **4 spaces** for C indentation
- Follow existing Linux kernel code style
- Avoid massive formatting changes in feature PRs
- Include comments for non-obvious code

---

## 📅 Roadmap

- [ ] Complete tested support for kernel 7.x
- [ ] Production-ready Bluetooth driver (see `bluetooth` branch)
- [ ] Native packaging for more distros (Debian, Fedora RPM)
- [ ] Web-based configuration for driver parameters
- [ ] Automated CI/CD tests
- [ ] Internal API documentation

---

## 📜 License and Credits

### License

This project is licensed under **GPL v2**. See [LICENSE](./LICENSE) for full details.

### Maintainer

- **[RicknotDev](https://github.com/RicknotDev)** — Adaptation, compatibility, and maintenance

### Credits

This driver is based on the original AIC8800D80 driver code. Modifications include:
- Adaptation for recent Linux kernels
- Support for multiple distributions
- Automatic installation with DKMS
- Improvements in compatibility and diagnostics

### Bluetooth branch

For Bluetooth support, see the [bluetooth branch](https://github.com/RicknotDev/aic8800d80/tree/bluetooth) of this project.

---

---

<div align="center">

# 🌐 SECCIÓN EN ESPAÑOL

</div>

---

# 🛜 Driver AIC8800D80 para Linux

[![Licencia: GPL v2](https://img.shields.io/badge/Licencia-GPLv2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.es.html)
[![Soporte de Kernel](https://img.shields.io/badge/Kernel-6.x-green.svg)](https://kernel.org/)
[![Distros Soportadas](https://img.shields.io/badge/Distros-8-blueviolet.svg)](#-compatibilidad--distros-y-gestores-de-paquetes)
[![Lenguaje](https://img.shields.io/badge/Lenguaje-C-00599C.svg)](https://es.wikipedia.org/wiki/C_(lenguaje_de_programaci%C3%B3n))
[![Mantenido por](https://img.shields.io/badge/Mantenido%20por-RicknotDev-brightgreen)](https://github.com/RicknotDev)

Driver universal de Linux para chipsets Wi-Fi AIC8800D80 con soporte DKMS y multi-distribución.

---

## 📋 Descripción

Este proyecto proporciona un **driver completo de kernel** para dispositivos Wi-Fi basados en el chipset **AIC8800D80**, compatible con tarjetas como Tenda U11 y AX913B. El driver incluye:

- **Instalación automática** mediante DKMS para mantener compatibilidad después de actualizaciones de kernel
- **Soporte multiplataforma** para 8 distribuciones Linux principales
- **Firmware integrado** con configuraciones para múltiples variantes de chipset
- **Reglas udev automáticas** para mejor integración del sistema

### ¿Por qué usar este driver?

- ✅ Compatible con kernels **6.x** (7.x con `--force`)
- ✅ Instalación **automática** en Debian, Fedora, Arch, Alpine y más
- ✅ **Sin dependencias ocultas** — detecta automáticamente lo que necesitas
- ✅ Soporte para **Vendor ID 368B** (clones Pandora)
- ✅ **DKMS integrado** — se reinstala automáticamente tras actualizar el kernel

---

## ⚡ Características Principales

- 🔧 **Instalación automática con DKMS** — se recompila tras actualizaciones de kernel
- 📦 **Firmware preempaquetado** para variantes D80, D80N, D80X2, DC, DLN
- 🐧 **8 distribuciones soportadas** — Debian, Fedora, Arch, Alpine, Void, Solus, openSUSE, CentOS
- 🛡️ **Detección de Secure Boot** — advierte si puede afectar la carga del módulo
- 🔌 **Reglas udev integradas** — soporte para modos de cambio USB automático
- 📊 **Logs detallados** — instalación con mensajes de diagnóstico claros
- ⏭️ **Compatibilidad de kernel** — verificación automática de versión antes de instalar

---

## 📊 Compatibilidad — Distros y Gestores de Paquetes

| Distribución         | Gestor de paquetes | Estado         | Notas                          |
|----------------------|--------------------|----------------|--------------------------------|
| Debian / Ubuntu      | apt                | ✅ Estable     | Probado en Ubuntu 25.04, Debian 12 |
| Fedora / RHEL        | dnf                | ✅ Estable     | RHEL 8+ compatible             |
| CentOS / RHEL legacy | yum                | ✅ Estable     | Requiere EPEL habilitado       |
| Arch Linux           | pacman             | ✅ Estable     | Incluye linux-headers          |
| openSUSE             | zypper             | ✅ Estable     | Leap y Tumbleweed             |
| Alpine Linux         | apk                | ✅ Estable     | Requiere edge repository       |
| Void Linux           | xbps-install       | ✅ Estable     | Compilación desde source       |
| Solus                | eopkg              | ✅ Estable     | Soporte experimental           |

### ℹ️ Distribuciones no detectadas

Si tu distro no está listada, puedes instalar las dependencias manualmente y luego ejecutar:

```bash
sudo ./install.sh --skip-deps
```

### Requisitos especiales por distro

- **Alpine Linux**: Requiere actualizar el repositorio con `edge`
- **Void Linux / Solus**: El compilador puede tardar más tiempo en la primera ejecución
- Todas las distros requieren acceso a `sudo` o permiso de root

---

## 📋 Requisitos Previos

### Software requerido

| Componente         | Versión mínima | Propósito                          |
|--------------------|---|----------------------------------------|
| Linux Kernel       | 6.0.0          | Sistema operativo base             |
| DKMS               | 3.0            | Gestor dinámico de módulos kernel  |
| Compilador (gcc)   | 9.x            | Herramientas de compilación        |
| Make               | 4.0            | Sistema de construcción            |
| Linux Headers      | Coincide con kernel | Archivos de desarrollo del kernel |

### Herramientas opcionales

- `mokutil` — para gestión de Secure Boot
- `udevadm` — para recargar reglas udev (generalmente incluido)

### Espacio en disco

- **Mínimo**: 500 MB (driver + firmware)
- **Recomendado**: 2 GB (espacio para compilación)

---

## 🚀 Instalación

### Método 1: Instalación automática (Recomendado)

La forma más rápida para la mayoría de usuarios:

```bash
# 1. Clonar el repositorio
git clone https://github.com/RicknotDev/aic8800d80.git
cd aic8800d80

# 2. Hacer ejecutable el instalador
chmod +x install.sh

# 3. Ejecutar la instalación
sudo ./install.sh
```

El script detectará tu distro, instalará las dependencias necesarias y configurará DKMS automáticamente.

#### Opciones avanzadas del instalador

```bash
# Para kernels 7.x (no garantizado, bajo tu propio riesgo)
sudo ./install.sh --force

# Si ya instalaste las dependencias manualmente
sudo ./install.sh --skip-deps

# Ver ayuda completa
sudo ./install.sh --help
```

### Método 2: Instalación manual

Para usuarios avanzados o distribuciones no detectadas:

#### 2.1. Instalar dependencias

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y dkms build-essential linux-headers-$(uname -r)

# Fedora/RHEL
sudo dnf install -y dkms make gcc kernel-devel kernel-headers

# Arch
sudo pacman -S dkms base-devel linux-headers

# Alpine
sudo apk update && sudo apk add dkms build-base linux-headers
```

#### 2.2. Copiar firmware

```bash
# Limpiar firmware antiguo (IMPORTANTE)
sudo rm -rf /lib/firmware/aic8800*

# Copiar el nuevo firmware
sudo cp -r ./fw/aic8800D80 /lib/firmware/
```

#### 2.3. Copiar reglas udev

```bash
sudo cp aic.rules /usr/lib/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

#### 2.4. Compilar e instalar con DKMS

```bash
# Navegar al directorio del driver
cd drivers/aic8800

# Compilar
make

# Instalar
sudo make install

# (Opcional) Generar DKMS config si no existe
sudo dkms add -m aic8800 -v 1.0.0
sudo dkms build -m aic8800 -v 1.0.0
sudo dkms install -m aic8800 -v 1.0.0
```

---

## 💻 Uso / Inicio Rápido

### Cargar el driver

```bash
# Cargar el módulo manualmente
sudo modprobe aic8800_fdrv
```

El driver se cargará automáticamente al arrancar después de la instalación.

### Verificar que funciona

```bash
# Verificar que el módulo está cargado
lsmod | grep aic

# Deberías ver algo como:
# aic8800_fdrv    536576  0
# cfg80211       1146880  1 aic8800_fdrv
# aic_load_fw     69632  1 aic8800_fdrv
```

### Buscar y conectar a redes Wi-Fi

```bash
# Listar interfaces de red disponibles
iwconfig

# Con NetworkManager (GNOME/KDE)
nmcli device
nmcli connection up <SSID>

# Con iwd (alternativa más moderna)
iwctl station wlan0 connect <SSID>
```

### Diagnosticar problemas

```bash
# Ver logs del kernel en tiempo real
sudo dmesg -w | grep aic

# Ver estado detallado del driver
cat /sys/class/net/wlan0/phy80211/name

# Comprobar si el dispositivo está en modo descarga/carga
lsusb | grep aic
```

---

## ⚙️ Configuración

### Parámetros del driver

El driver carga archivos de configuración desde la carpeta `fw/`:

```
fw/
├── aic8800D80/          # Variante estándar
│   ├── aic_userconfig_8800d80.txt
│   ├── aic_powerlimit_8800d80.txt
│   └── (otros archivos de firmware)
├── aic8800D80N/         # Variante N
├── aic8800D80X2/        # Variante X2
├── aic8800DC/           # Variante DC
└── aic8800DLN/          # Variante DLN
```

Para usar una configuración específica, edita el archivo `aic_userconfig_*.txt` correspondiente a tu variante antes de instalar.

### Variables de kernel (módulo)

Después de instalar, puedes ajustar parámetros al cargar el módulo:

```bash
# Ejemplo: cargar con parámetro de ruta de firmware personalizado
sudo modprobe aic8800_fdrv aic_fw_path=/custom/fw/path

# Para ver todos los parámetros disponibles
modinfo aic8800_fdrv
```

### Desinstalar el driver

```bash
# Si se instaló con DKMS
sudo dkms remove aic8800/1.0.0 --all
sudo rm -rf /lib/firmware/aic8800*
sudo rm /usr/lib/udev/rules.d/aic.rules
sudo udevadm control --reload-rules

# Si se instaló manualmente
cd drivers/aic8800
sudo make uninstall
```

---

## 📁 Estructura del Proyecto

```
aic8800d80/
├── install.sh                    # Instalador automático universal
├── diagnostic_build.sh           # Script de diagnóstico
├── dkms.conf                     # Configuración de DKMS
├── README.md                     # Este archivo
├── drivers/
│   └── aic8800/
│       ├── Makefile              # Build script principal
│       ├── aic_load_fw/          # Módulo de carga de firmware
│       │   ├── aic_bluetooth_main.c
│       │   ├── aicwf_usb.c
│       │   └── (+ archivos de compatibilidad)
│       └── aic8800_fdrv/         # Módulo de driver Wi-Fi
│           ├── rwnx_main.c       # Punto de entrada
│           ├── rwnx_tx.c         # Transmisión
│           ├── rwnx_rx.c         # Recepción
│           └── (+ archivos de soporte)
├── fw/                           # Firmware binario
│   ├── aic8800D80/
│   ├── aic8800D80N/
│   ├── aic8800D80X2/
│   ├── aic8800DC/
│   └── aic8800DLN/
├── aic.rules                     # Reglas udev
├── usb_modeswitch/              # Configuración de cambio de modo USB
└── bazzite/                      # Empaquetado para Bazzite (rpm-ostree)
```

### Módulos principales

- **aic_load_fw**: Carga el firmware en el dispositivo USB y gestiona Bluetooth
- **aic8800_fdrv**: Driver Wi-Fi principal que interactúa con cfg80211 y mac80211

---

## 🧪 Tests y Diagnóstico

### Ejecutar diagnóstico completo

```bash
# El script verifica estructura, DKMS, firmware, y kernel
chmod +x diagnostic_build.sh
sudo ./diagnostic_build.sh
```

Este script valida:
- ✅ Presencia de archivos de compilación
- ✅ Configuración de DKMS
- ✅ Firmware instalado correctamente
- ✅ Compatibilidad de kernel y herramientas
- ✅ Logs de compilación (si existen)

### Probar compilación manual

```bash
cd drivers/aic8800
make clean
make VERBOSE=1  # Mostrar detalles de compilación
```

---

## 🤝 Contribución

Las contribuciones son bienvenidas. Para contribuir:

### 1. Hacer un fork del proyecto

```bash
git clone https://github.com/RicknotDev/aic8800d80.git
cd aic8800d80
```

### 2. Crear una rama para tu feature

```bash
git checkout -b feature/mi-mejora
```

### 3. Hacer commits con mensajes claros

```bash
git commit -m "feat: añadir soporte para kernel 7.x"
git commit -m "fix: resolver problema de carga en Alpine"
```

### 4. Subir cambios y crear un Pull Request

```bash
git push origin feature/mi-mejora
```

Luego abre un PR en GitHub describiendo:
- Qué problema resuelve
- Cómo se probó
- Cambios en comportamiento (si los hay)

### Convenciones de código

- Usa **espacios de 4** para indentación en C
- Sigue el estilo existente del kernel Linux
- Evita cambios de formato masivos en PRs de funcionalidad
- Incluye comentarios para código no obvio

---

## 📅 Roadmap

- [ ] Soporte completo y probado para kernel 7.x
- [ ] Driver Bluetooth de producción (rama `bluetooth`)
- [ ] Empaquetado nativo para más distros (Debian, Fedora RPM)
- [ ] Configuración web para parámetros del driver
- [ ] Tests automatizados en CI/CD
- [ ] Documentación de API interna

---

## 📜 Licencia y Créditos

### Licencia

Este proyecto está bajo licencia **GPL v2**. Ver [LICENSE](./LICENSE) para detalles completos.

### Mantenedor

- **[RicknotDev](https://github.com/RicknotDev)** — Adaptación, compatibilidad y mantenimiento

### Créditos

Este driver está basado en el código original del driver AIC8800D80 de Tenda. Las modificaciones incluyen:
- Adaptación para kernels Linux más recientes
- Soporte para múltiples distribuciones
- Instalación automática con DKMS
- Mejoras en compatibilidad y diagnóstico

### Rama Bluetooth

Para soporte de Bluetooth, ver la [rama `bluetooth`](https://github.com/RicknotDev/aic8800d80/tree/bluetooth) del proyecto.

---

## 📞 Soporte

Si quieres reportar bugs o contribuir, [abre un issue](https://github.com/RicknotDev/aic8800d80/issues) o [envía un PR](https://github.com/RicknotDev/aic8800d80/pulls).
