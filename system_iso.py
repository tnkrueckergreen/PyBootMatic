#!/usr/bin/env python3

import argparse
import logging
import os
import subprocess
import sys
import shutil
import tempfile
from rich.console import Console
from rich.progress import Progress, BarColumn, TimeRemainingColumn

console = Console()

def create_system_iso(output_iso_path, exclude_dirs, bootloader_command=None):
    """Creates a polished ISO image of the current Linux system, excluding specified directories.

    Args:
        output_iso_path (str): Path to create the ISO image.
        exclude_dirs (list): Directories to exclude from the ISO.
        bootloader_command (str, optional): Command to install the bootloader.
    """
    console.print("[bold cyan]System ISO Creator[/bold cyan]")
    console.print("[italic]This script will create a polished ISO image of your Linux system.[/italic]\n")

    # Validate output path
    if os.path.exists(output_iso_path):
        console.print(f"[yellow]Warning:[/yellow] The file '[cyan]{output_iso_path}[/cyan]' already exists.")
        overwrite_choice = console.input("[yellow]Do you want to overwrite it? (y/N):[/yellow] ").lower()
        if overwrite_choice not in ("y", "yes"):
            console.print("[red]Aborting![/red]")
            sys.exit(1)

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            console.print("\n[bold green]Preparing files...[/bold green]")

            # Copy system files with detailed progress
            with Progress(
                "[progress.description]{task.description}",
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task("[green]Copying system files...", total=100)
                rsync_command = ["rsync", "-axHAX", "--exclude", ",".join(exclude_dirs), "/", temp_dir]
                subprocess.run(rsync_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                progress.update(task, completed=100)

            console.print("\n[bold green]Creating ISO image...[/bold green]")

            # Create ISO with detailed progress
            with Progress(
                "[progress.description]{task.description}",
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task("[green]Generating ISO...", total=100)
                genisoimage_command = ["genisoimage", "-o", output_iso_path, "-R", temp_dir]
                subprocess.run(genisoimage_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                progress.update(task, completed=100)

            # Install bootloader (if provided)
            if bootloader_command:
                console.print("\n[bold green]Installing bootloader...[/bold green]")
                subprocess.run(bootloader_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

            console.print(f"\n[bold green]Success![/bold green] Your ISO is ready at: [cyan]{output_iso_path}[/cyan]")

        except subprocess.CalledProcessError as error:
            console.print(f"\n[red]Error creating ISO:[/red] {error}")
            sys.exit(1)
        except Exception as e:
            console.print(f"\n[red]Unexpected error:[/red] {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Create a polished ISO image of your Linux system")
    parser.add_argument("output_iso", help="Path to create the ISO image")
    parser.add_argument("--exclude", action="append", default=[], help="Directories to exclude")
    parser.add_argument("--bootloader", help="Command to install the bootloader")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    # Set logging level
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # Check for root privileges
    if not os.geteuid() == 0:
        console.print("[red]Error![/red] This script requires root privileges. Please run with sudo.")
        sys.exit(1)

    # Check for required tools
    required_tools = ["genisoimage"]
    for tool in required_tools:
        if not shutil.which(tool):
            console.print(f"[red]Error![/red] Missing required tool: [bold]{tool}[/bold]. Please install it.")
            sys.exit(1)

    create_system_iso(args.output_iso, args.exclude, args.bootloader)

if __name__ == "__main__":
    main()
