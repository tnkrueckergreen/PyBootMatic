import apt
import shutil 
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

class PyBootMatic:

    def build_linux(self, iso_path: Path):
        self.make_iso(iso_path, minimal=True)

    def make_iso(self, iso_path: Path, *, minimal=False): 
        with tempfile.TemporaryDirectory() as td:
            build_dir = Path(td) / "build"
            build_dir.mkdir()
            
            self.copy_fs(build_dir)
            
            kernel, initrd = self.setup_bootloader(build_dir)
            self.make_grub_cfg(build_dir, kernel, initrd, iso_path)
            self.make_iso_image(build_dir, iso_path)
            
    def setup_bootloader(self, build_dir: Path) -> tuple[str, str]:
        kernel = self.get_kernel(build_dir)  
        if not kernel:
            kernel = self.install_kernel(build_dir)
            
        initrd = self.get_initrd(build_dir)
        if not initrd:
            initrd = self.install_initrd(build_dir)
            
        return kernel, initrd
            
    def copy_fs(self, dest_dir: Path): 
        subprocess.run(["rsync", "-a", "/.", str(dest_dir)])
        
    def install_kernel(self, build_dir: Path) -> str:
        cache = apt.Cache()
        kernel = self.find_latest_kernel(cache)
        kernel.mark_install() 
        cache.commit()
         
        subprocess.run(["update-grub"], check=True) 
        
        kernel_fname = "vmlinuz-{}".format(kernel.version)     
        shutil.copy("/boot/"+kernel_fname, build_dir/"boot")
         
        return kernel_fname  

    def find_latest_kernel(self, cache: apt.Cache) -> apt.Package:
        packages = (p for p in cache if p.name.startswith("linux-image")) 
        return max(packages, key=lambda p: apt.version_compare(p.candidate.version, "<"))
        
    def get_kernel(self, build_dir: Path) -> Optional[str]:
        for fname in build_dir.glob("boot/vmlinuz*"):
            return fname.name
        return None
    
    def get_initrd(self, build_dir: Path) -> Optional[str]:
        paths = build_dir.glob("boot/initrd*")
        if paths:
            return paths[0].name
        return None       
        
    def install_initrd(self, build_dir: Path) -> str:
        cache = apt.Cache()
        pkg = cache["initramfs-tools"]
        pkg.mark_install()
        cache.commit()
        
        subprocess.run(["update-initramfs", "-u"], check=True) 
        
        shutil.copy("/boot/initrd.img", build_dir/"boot") 
        
        return "initrd.img"
        
    def make_grub_cfg(self, build_dir: Path, kernel: str, initrd: str, iso_path: Path):
        cfg = f"""\
            set default=0
            menuentry "Try System" {{
                linux /boot/{kernel}
                initrd /boot/{initrd}
            }}
            """
            
        (build_dir/"boot/grub").mkdir(parents=True, exist_ok=True) 
        
        with (build_dir/"boot/grub/grub.cfg").open("w") as f:
            f.write(cfg)
            
    def make_iso_image(self, build_dir: Path, iso_path: Path):
        subprocess.run(["xorriso", 
            "-as", "mkisofs",
            "-o", str(iso_path),
            build_dir
        ], check=True)
        
def main():
    iso_path = Path("/tmp/my.iso") 
    app = PyBootMatic()
    app.build_linux(iso_path)
    
if __name__ == "__main__":
    main()
