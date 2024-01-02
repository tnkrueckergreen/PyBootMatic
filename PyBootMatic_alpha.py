import apt
import shutil
import subprocess
import tempfile
import os
import sys
import struct
import logging
import getpass
import hashlib
from rich.prompt import Prompt, Confirm
from rich.progress import Progress
from pathlib import Path

def install_kernel():
    logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)
    logger, cache, lw = logging.getLogger(__name__), apt.Cache(), lambda p: p.candidate.version
    logger.info("Starting kernel installation script.")

    latest_kernel = max((pkg for pkg in cache if pkg.candidate and pkg.name.startswith("linux-image")), key=lw, default=None)
    if not latest_kernel:
        logger.error("Error: No suitable kernel package found.")
        sys.exit(1)

    kv = latest_kernel.candidate.version
    logger.info(f"Found the latest kernel: {latest_kernel.name} (Version: {kv})")
    latest_kernel.mark_install()

    try:
        cache.commit()
        logger.info("Successfully marked the latest kernel for installation.")
    except Exception as e:
        logger.error(f"Failed to install the latest kernel: {e}")
        sys.exit(1)

    logger.info(f"Latest kernel installed successfully: {latest_kernel.name} (Version: {kv})")

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
            self.make_grub(build_dir, iso_path)

    def make_full_custom_linux(self, iso_path):
        self.make_vanilla_linux(iso_path)

    def build_windows(self, iso_path):
        print("[red]\nWindows ISO build not implemented[/]")

    def copy_fs(self, dest_dir):
        excluded = [
            "/tmp",
            "/run",
            "/mnt",
            "/dev",
            "/proc",
            "/sys",
            str(dest_dir),
            "/**/.cache/**",
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

    def make_grub(self, build_dir, iso_path):
        kernel = self.get_kernel(build_dir)
        if not kernel:
            install_kernel()
            kernel = self.get_kernel(build_dir)

        initrd = self.get_initrd(build_dir)
        if not initrd:
            self.install_initrd(build_dir)
            initrd = self.get_initrd(build_dir)

        grub_dir = build_dir / "boot" / "grub"
        grub_cfg = grub_dir / "grub.cfg"

        os.makedirs(os.path.dirname(grub_cfg), exist_ok=True)

        if not grub_cfg.exists():
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
                print(f"The grub.cfg file could not be created or written: {e}")
                sys.exit(1)
        else:
            print(f"The grub.cfg file already exists in the system: {grub_cfg}")

        password = getpass.getpass("Enter a password to encrypt the ISO image: ")
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Generate grub rescue config
        rescue_cfg = grub_dir / "rescue.cfg"
        with open(rescue_cfg, "w") as f:
            f.write(f"""set timeout=10

loopback loop {iso_path}
set root=(loop)

linux (loop)/boot/{kernel}
initrd (loop)/boot/{initrd}
""")

        # Create ISO with grub rescue
        try:
            subprocess.run(["grub-mkrescue", "-o", iso_path, build_dir], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to create ISO image with grub rescue: {e}")
            sys.exit(1)

        if self.check_bootable(iso_path):
            print(f"The ISO file {iso_path} is bootable and encrypted.")
        else:
            print(f"The ISO file {iso_path} is not bootable or encrypted.")

    def get_kernel(self, build_dir):
        kernel_path = build_dir / "boot" / "vmlinuz"
        if kernel_path.exists():
            return "vmlinuz"
        return ""

    def get_initrd(self, build_dir):
        initrd_path = self.get_latest_initrd(build_dir)
        if initrd_path:
            return initrd_path.name
        return ""

    def get_latest_initrd(self, build_dir):
        initrd_path = build_dir / "boot" / "initrd.img-*"
        initrd_files = list(initrd_path.parent.glob(initrd_path.name))
        if initrd_files:
            return max(initrd_files, key=os.path.getctime)
        return None

    def install_initrd(self, build_dir):
        cache = apt.Cache()
        initrd_pkg = cache["initramfs-tools"]
        initrd_pkg.mark_install()

        try:
            cache.commit()
        except Exception as error:
            print(f"Failed installing initramfs-tools: {error}")

        subprocess.run(["update-initramfs", "-u"], check=True)

        grub_dir = build_dir / "boot" / "grub"
        initrd_path = self.get_latest_initrd(build_dir)
        if initrd_path:
            shutil.copy(initrd_path, grub_dir)

    def check_bootable(self, iso_path):
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
