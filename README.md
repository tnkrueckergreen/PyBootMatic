# PyBootMatic

PyBootMatic is a script for building customized Linux and Windows ISO images. It uses Rich for enhanced console output and requires several dependencies.

## Installation

### 1. Python

Ensure that Python is installed on your system. You can download it from the [official Python website](https://www.python.org/). Or, for Debain-based systems:
```bash
sudo apt install python3-pip
```

### 2. Pip

If you don't have `pip` installed, you can install it by following the instructions on the [official pip website](https://pip.pypa.io/en/stable/installation/).

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

Follow the prompts to build Linux or Windows ISO images.

## Notes

- Ensure that you have root privileges before running the script.

- Additional dependencies may be required based on your system configuration. If you encounter errors, you may have unmet dependencies.
