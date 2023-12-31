# PyBootMatic

PyBootMatic is a script for building customized Linux and Windows ISO images. It uses Rich for enhanced console output and requires several dependencies.

## Installation

### 1. Python

Ensure that Python is installed on your system. You can download it from the [official Python website](https://www.python.org/).

### 2. Rich Library

Install the Rich library using the following command:

```bash
pip install rich
```

### 3. Grub

The script uses `grub-mkrescue` to create a bootable ISO. Install GRUB tools on your system. The installation process may vary; for example, on Debian-based systems:

```bash
sudo apt-get install grub-pc-bin
```

### 4. Rsync

The script uses the `rsync` command for copying the filesystem. Install it with the package manager appropriate for your system. For example, on Debian-based systems:

```bash
sudo apt-get install rsync
```

### 5. Xorriso

Install `xorriso` with the following command:

```bash
sudo apt-get install xorriso
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

- Additional dependencies may be required based on your system configuration. If you encounter errors, you might have unmet dependencies.
