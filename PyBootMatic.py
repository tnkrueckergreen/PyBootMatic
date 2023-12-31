from rich import print
from rich.progress import Progress
from rich.prompt import Prompt, Confirm
from pathlib import Path
import subprocess
import tempfile
import sys
import os
import shutil


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
                subprocess.run(
                    [
                        rsync_path := shutil.which("rsync"),  # Get the path of the rsync command
                        "-aAXxv",
                        "--no-inc-recursive",  # Prevent recursive copying into identical subdirectories
                        "--ignore-errors",  # Ignore errors in copying special files
                        "--ignore-missing-args",  # Skip files that are missing or in use by the system
                        "--no-acls",  # Disable ACL copying
                        *["--exclude=" + str(pattern) for pattern in excluded],  # Use list comprehension to generate the exclude options
                        "/",
                        str(dest_dir),
                    ],
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                progress.update(task, description="[red]Error: rsync failed[/]")
                print(f"rsync error: {e}")
                sys.exit(1)
            progress.update(task, advance=1000)

    def make_grub(self, build_dir, iso_path):
        with Progress() as progress:
            task = progress.add_task("[blue]Installing bootloader[/]", total=1000)
            subprocess.run(["grub-mkrescue", "-o", str(iso_path), str(build_dir)], check=True)
            progress.update(task, advance=1000)


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
