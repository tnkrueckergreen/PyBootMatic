# System ISO Creator

Create a polished ISO image of your Linux system effortlessly.

![System ISO Creator](demo.gif)

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The System ISO Creator is a tool that helps you create a snapshot of your Linux system, making it easy to back up or share without including personal data.

## Features

- 🌈 **User-friendly Interface:** Easy-to-follow steps for creating an ISO image.
- 🔄 **Progress Bars:** Visual indicators for copying files, creating ISO, and installing the bootloader.
- 📂 **Exclude Directories:** Choose specific folders to exclude from the ISO.
- ⚙️ **Bootloader Installation:** Optional installation of a bootloader for system bootability.
- 🔒 **Root Privileges Check:** Ensures the script has the necessary permissions.

## Prerequisites

Before using the System ISO Creator, make sure you have the following:

- A computer running a Linux operating system.
- [Python](https://www.python.org/downloads/) installed.
- The `genisoimage` tool, usually available through your system's package manager.

## Installation

1. **Download the Script:**
    ```bash
git clone https://github.com/tnkrueckergreen/SystemISO.git
cd SystemISO

    ```

2. **Install Required Packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Run the Script:**
    ```bash
    sudo ./system_iso_creator.py OUTPUT_ISO_PATH --exclude EXCLUDE_DIR1 --exclude EXCLUDE_DIR2 --bootloader "BOOTLOADER_COMMAND"
    ```

    Replace:
    - `OUTPUT_ISO_PATH` with the path where you want to save the ISO.
    - `EXCLUDE_DIR1` and `EXCLUDE_DIR2` with any folders you want to leave out.
    - `"BOOTLOADER_COMMAND"` with the bootloader installation command (if needed).

2. **Follow On-Screen Instructions:**
    The script will guide you through the process with easy-to-understand prompts and progress bars.

## FAQ

### Q: Can I use this on any Linux distribution?

Yes, the System ISO Creator is designed to work on most Linux distributions.

### Q: How do I install the bootloader?

If you're unsure about the bootloader, you can skip providing the `"BOOTLOADER_COMMAND"` during usage. The script will let you know if it's needed.

## Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

