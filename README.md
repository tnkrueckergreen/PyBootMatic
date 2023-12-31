# PyBootMatic

PyBootMatic is a script for building bootable Linux ISO images from your current system. It is quite simple to use. (Windows ISO creation is not yet implemented.) It uses Rich for enhanced console output and requires several dependencies. The stable version is functional but has not been tested extensively enough to confirm if the created ISO is reliably bootable. However, it can be used to generate a backup system image. This page will be updated as the script undergoes further testing. The alpha version configures the kernel, grub.cfg and other critical files needed for a bootable ISO. Further development is still required for both versions.

## Installation

### 1. Python

Ensure that Python is installed on your system. You can download it from the [official Python website](https://www.python.org/). 

### 2. Pip

If you don't have `pip` installed, you can install it by following the instructions on the [official pip website](https://pip.pypa.io/en/stable/installation/). Or, on Debian-based systems:
```bash
sudo apt install python3-pip
```

### 3. Rich Library

Install the Rich library using the following command:

```bash
sudo pip install rich
```

### 4. Grub

The script uses `grub-mkrescue` to create a bootable ISO. Install GRUB tools on your system. The installation process may vary; for example, on Debian-based systems:

```bash
sudo apt install grub-pc-bin
```

### 5. Rsync

The script uses the `rsync` command for copying the filesystem. Install it with the package manager appropriate for your system. For example, on Debian-based systems:

```bash
sudo apt install rsync
```

### 6. Xorriso

Install `xorriso` with the following command:

```bash
sudo apt install xorriso
```

## Usage

1. Clone this repository:

```bash
git clone https://github.com/tnkrueckergreen/PyBootMatic.git
cd PyBootMatic
```

2. Run the script:

```bash
sudo python3 PyBootMatic.py
```
If you wish to try the new alpha version (very bug-prone at the moment):
```bash
sudo python3 PyBootMatic_alpha.py
```

Prepare for problems, work needs to be done!

## Notes

- Ensure that you have root privileges before running the script.

- Additional dependencies may be required based on your system configuration. If you encounter errors, you may have unmet dependencies.
