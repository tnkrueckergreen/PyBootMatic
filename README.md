# SystemISO

SystemISO is a Python script that creates a polished ISO image of your Linux system. This script allows you to customize the ISO creation process by excluding specific directories and optionally installing a bootloader.

## Features

- **Polished ISO Creation**: Easily generate an ISO image of your Linux system with a polished and user-friendly script.
- **Directory Exclusion**: Exclude specific directories from the ISO to tailor it to your needs.
- **Bootloader Installation (Optional)**: Install a bootloader to make the ISO bootable (optional, provide your own bootloader command).

## Usage

```bash
sudo ./system_iso.py OUTPUT_ISO_PATH --exclude DIR1 --exclude DIR2 --bootloader BOOTLOADER_COMMAND
```

- `OUTPUT_ISO_PATH`: Path where the ISO image will be created.
- `--exclude DIR1`: Exclude directory DIR1 from the ISO. You can provide multiple `--exclude` flags for additional directories.
- `--bootloader BOOTLOADER_COMMAND`: (Optional) Command to install the bootloader for creating a bootable ISO.

## Prerequisites

- Root privileges (use `sudo` to run the script).
- Required tool: `genisoimage` (install it using your system's package manager).

## Example

```bash
sudo ./system_iso.py my_system.iso --exclude /home --bootloader "grub-install /dev/sdX"
```

This example creates an ISO named `my_system.iso`, excluding the `/home` directory and installing the Grub bootloader.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
