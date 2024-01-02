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


It looks like there are a few issues that could cause the ISO to not have the kernel or initrd:

1. The `get_kernel()` and `get_initrd()` methods are not actually copying the kernel/initrd into the ISO build directory. They are just checking if the files exist and returning the filenames. So this would cause empty files in the ISO.

2. The `install_initrd()` method installs `initramfs-tools` but doesn't actually copy the generated initrd into the build directory.

3. When calling `grub-mkrescue`, it is only passed the build directory, not the full path to the kernel/initrd files. So Grub may not be able to find those files to add them to the ISO.

Here are some suggestions to fix it:

1. Update `get_kernel()` and `get_initrd()` to actually copy the files into the build directory if found rather than just returning the filenames.

2. In `install_initrd()`, copy the generated initrd file into the build directory after running `update-initramfs`.

3. Pass the full paths to the kernel and initrd files to `grub-mkrescue`, rather than just the build directory:

```
grub-mkrescue -o iso_path /full/path/to/vmlinuz /full/path/to/initrd.img build_dir
```

This will explicitly tell Grub where to find those critical boot files.

Let me know if any part of the suggestions needs more clarification!
