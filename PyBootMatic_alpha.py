from rich import print
from rich.progress import Progress
from rich.prompt import Prompt, Confirm
from pathlib import Path
import subprocess
import tempfile
import sys
import os
import shutil
import struct
import logging
import getpass
import hashlib
import apt

# Set up the logging module
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class PyBootMatic:

    def __init__(self):
        self.confirm_root_privileges()

    def confirm_root_privileges(self):
        if os.getuid() != 0:
            print("[bold red]Root privileges required to build ISO[/]")
            try:
                os.execvp("sudo", ["sudo"] + sys.argv)
            except Exception as e:
                print(f"Could not escalate privileges - {e}")
                sys.exit(1)

    def build_linux(self, iso_path):
        response = Prompt.ask("How much customization is needed?", choices=["minimal", "moderate", "full"])
        if response == "minimal":
            self.make_vanilla_linux(iso_path)
        elif response == "moderate":
            self.make_vanilla_linux(iso_path)
        else:
            self.make_full_custom_linux(iso_path)
        print(f"[green]\nLinux ISO image built at: {iso_path}[/]")

    def make_vanilla_linux(self, iso_path):
        with tempfile.TemporaryDirectory() as td:
            build_dir = Path(td) / "build"
            build_dir.mkdir()
            self.copy_fs(build_dir)
            make_grub(build_dir, iso_path)

    def make_full_custom_linux(self, iso_path):
        self.make_vanilla_linux(iso_path)

    def build_windows(self, iso_path):
        print("[red]\nWindows ISO build not implemented[/]")

    def copy_fs(self, dest_dir):
        """Copies the filesystem to the destination directory, excluding specified directories."""
        excluded = [
            "/tmp",
            "/run",
            "/mnt",
            "/dev",
            "/proc",
            "/sys",
            str(dest_dir),  # Exclude the build directory itself
            "/**/.cache/**",  # Exclude all ".cache" directories recursively
        ]
        with Progress() as progress:
            task = progress.add_task("[green]Cloning filesystem[/]", total=1000)
            try:
                output = subprocess.check_output(
                    [
                        rsync_path := shutil.which("rsync"),
                        "-aAXxv",
                        "--no-inc-recursive",
                        "--ignore-errors",
                        "--ignore-missing-args",
                        "--no-acls",
                        *["--exclude=" + str(pattern) for pattern in excluded],
                        "/",
                        str(dest_dir),
                    ],
                    stderr=subprocess.STDOUT,
                )
                lines = output.decode().split("\n")
                lines = [line for line in lines if not line.startswith("sending incremental file list")]
                output = "\n".join(lines)
                print(output)
            except subprocess.CalledProcessError as e:
                progress.update(task, description="[red]Error: rsync failed[/]")
                print(f"rsync error: {e}")
                sys.exit(1)
            progress.update(task, advance=1000)


def make_grub(build_dir, iso_path):
    """Create a bootable ISO image with GRUB bootloader and a menu."""
    if not os.path.exists(build_dir) or not os.path.isdir(build_dir):
        raise ValueError(f"The build directory {build_dir} does not exist or is not a directory.")
    if not str(iso_path) or not str(iso_path).endswith(".iso"):
        raise ValueError(f"The iso path {iso_path} is not valid or does not have the .iso extension.")
    with Progress() as progress:
        task = progress.add_task("[blue]Installing bootloader[/]", total=1000)
        find_cmd = ["find", "/", "-xdev", "-type", "f", "-name", "grub.cfg", "-quit"]
        try:
            grub_cfg = subprocess.check_output(find_cmd).decode().strip()
        except subprocess.CalledProcessError as e:
            raise subprocess.CalledProcessError(e.returncode, e.cmd, e.output)
        if not grub_cfg:
            logging.info("The grub.cfg file does not exist in the system. Generating a new one.")
            grub_dir = os.path.join(build_dir, "boot", "grub")
            os.makedirs(grub_dir, exist_ok=True)
            grub_cfg = os.path.join(grub_dir, "grub.cfg")
            kernel = os.path.basename(os.path.join(build_dir, "boot", "vmlinuz"))
            initrd = os.path.basename(os.path.join(build_dir, "boot", "initrd.img"))
            try:
                with open(grub_cfg, "w") as f:
                    f.write(f"""# This is the grub.cfg file for the ISO image
set timeout=10
set default=0

menuentry "Try the system" {{
    loopback loop /iso/boot.iso
    linux (loop)/boot/{kernel}
    initrd (loop)/boot/{initrd}
}}

menuentry "Install the system" {{
    loopback loop /iso/boot.iso
    linux (loop)/boot/{kernel} install
    initrd (loop)/boot/{initrd}
}}""")
            except IOError as e:
                raise IOError(f"The grub.cfg file could not be created or written: {e}")
        else:
            logging.info(f"The grub.cfg file exists in the system: {grub_cfg}")
            grub_dir = os.path.join(build_dir, "boot", "grub")
            shutil.copy(grub_cfg, grub_dir)

        password = getpass.getpass("Enter a password to encrypt the ISO image: ")
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        xorriso_cmd = ["xorriso", "-as", "mkisofs", "-o", iso_path, "-V", "ENCRYPTED_ISO", "-isohybrid-mbr", "/usr/lib/ISOLINUX/isohdpfx.bin", "-c", "isolinux/boot.cat", "-b", "isolinux/isolinux.bin", "-no-emul-boot", "-boot-load-size", "4", "-boot-info-table", "-eltorito-alt-boot", "-e", "--", "-no-emul-boot", "-isohybrid-gpt-basdat", "-isohybrid-apm-hfsplus", "-encrypt", "aes256", password_hash, build_dir]
        try:
            subprocess.run(xorriso_cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise subprocess.CalledProcessError(e.returncode, e.cmd, e.output)
        progress.update(task, advance=1000)

        if check_bootable(iso_path):
            logging.info(f"The ISO file {iso_path} is bootable and encrypted.")
        else:
            logging.error(f"The ISO file {iso_path} is not bootable or encrypted.")


def check_bootable(iso_path):
    """Check if the ISO file is bootable by reading the boot sector."""
    if not os.path.exists(iso_path) or not os.path.isfile(iso_path):
        raise FileNotFoundError(f"The ISO file {iso_path} does not exist or is not a file.")
    try:
        with open(iso_path, "rb") as iso_file:
            boot_sector = iso_file.read(512)
            magic_number = struct.unpack("<H", boot_sector[-2:])[0]
            return magic_number == 0xAA55
    except IOError as e:
        raise IOError(f"The ISO file {iso_path} is corrupted or unreadable: {e}")


def main():
    app = PyBootMatic()
    system = Prompt.ask("Build ISO for which OS?", choices=["Linux", "Windows"])
    iso_path = Path(Prompt.ask("Enter output ISO file path"))
    if not iso_path.suffix == ".iso":
        iso_path = iso_path.with_suffix(".iso")

    if Confirm.ask("Proceed with build?", default=True):
        if system == "Linux":
            app.build_linux(iso_path)
        else:
            app.build_windows(iso_path)


if __name__ == "__main__":
    main()
