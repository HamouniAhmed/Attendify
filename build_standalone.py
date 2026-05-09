# build_standalone.py
import os
import sys
import shutil
import subprocess
from pathlib import Path

class AttendifyBuilder:
    def __init__(self):
        self.project_dir = Path.cwd()
        self.dist_dir = self.project_dir / "dist"
        self.build_dir = self.project_dir / "build"
        self.package_dir = self.project_dir / "Attendify_Portable"
        
    def clean_previous_builds(self):
        """Remove previous build artifacts"""
        print("🧹 Cleaning previous builds...")
        
        dirs_to_clean = [self.dist_dir, self.build_dir, self.package_dir]
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                    print(f"   ✓ Removed {dir_path}")
                except Exception as e:
                    print(f"   ⚠️  Could not remove {dir_path}: {e}")
                    # Try to continue anyway
        
        print("   ✓ Cleanup completed")
        return True
    
    def check_requirements(self):
        """Check if all required files exist"""
        print("🔍 Checking requirements...")
        
        required_files = [
            "launcher.py",
            "app/__init__.py",
            "app/config.py",
            "requirements.txt",
            "attendify.spec"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_dir / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print("✗ Missing required files:")
            for file in missing_files:
                print(f"   - {file}")
            return False
        
        print("   ✓ All required files found")
        return True
    
    def install_dependencies(self):
        """Install required dependencies"""
        print("📦 Installing dependencies...")
        
        try:
            # Check if requirements.txt exists
            req_file = self.project_dir / "requirements.txt"
            if not req_file.exists():
                print("   ⚠️  requirements.txt not found, skipping dependency installation")
                return True
            
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "-r", str(req_file)
            ], check=True, capture_output=True, text=True, cwd=str(self.project_dir))
            
            print("   ✓ Dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ✗ Failed to install dependencies:")
            print(f"   STDOUT: {e.stdout}")
            print(f"   STDERR: {e.stderr}")
            return False
        except Exception as e:
            print(f"   ✗ Dependency installation error: {e}")
            return False
    
    def build_executable(self):
        """Build the executable using PyInstaller"""
        print("🔨 Building executable...")
        
        try:
            # Use quotes around spec file path to handle spaces
            spec_path = str(self.project_dir / "attendify.spec")
            cmd = [sys.executable, "-m", "PyInstaller", spec_path, "--clean"]
            
            print(f"   Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.project_dir))
            
            if result.returncode == 0:
                print("   ✓ Executable built successfully")
                return True
            else:
                print(f"   ✗ Build failed:")
                print(f"   STDOUT: {result.stdout}")
                print(f"   STDERR: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ✗ Build error: {e}")
            return False
    
    def create_portable_package(self):
        """Create a portable package"""
        print("📦 Creating portable package...")
        
        try:
            # Create package directory
            self.package_dir.mkdir(exist_ok=True)
            
            # Copy executable
            exe_source = self.dist_dir / "Attendify.exe"
            exe_dest = self.package_dir / "Attendify.exe"
            
            if exe_source.exists():
                shutil.copy2(exe_source, exe_dest)
                print("   ✓ Executable copied")
            else:
                print("   ✗ Executable not found")
                return False
            
            # Create data directory for user files
            data_dir = self.package_dir / "data"
            data_dir.mkdir(exist_ok=True)
            
            # Copy instance folder if exists
            if (self.project_dir / "instance").exists():
                shutil.copytree(
                    self.project_dir / "instance",
                    data_dir / "instance",
                    dirs_exist_ok=True
                )
                print("   ✓ Database files copied")
            
            # Copy uploads if exists
            uploads_source = self.project_dir / "app" / "static" / "uploads"
            if uploads_source.exists():
                uploads_dest = data_dir / "uploads"
                shutil.copytree(uploads_source, uploads_dest, dirs_exist_ok=True)
                print("   ✓ Upload files copied")
            
            return True
            
        except Exception as e:
            print(f"   ✗ Package creation failed: {e}")
            return False
    
    def create_startup_files(self):
        """Create startup files for the portable package"""
        print("📝 Creating startup files...")
        
        try:
            # Create start.bat
            bat_content = '''@echo off
title Attendify
echo.
echo ========================================
echo    ATTENDIFY LAUNCHER
echo ========================================
echo.
echo Starting Attendify...
echo Please wait while the system loads...
echo.

Attendify.exe
            
            bat_file = self.package_dir / "start.bat"
            with open(bat_file, 'w', encoding='utf-8') as f:
                f.write(bat_content)
            
            # Create README
            readme_content = '''# ATTENDIFY - PORTABLE VERSION

## How to Run:
1. Double-click "start.bat" to launch the system
2. Wait for the web browser to open automatically
3. If browser doesn't open, manually go to: http://127.0.0.1:5000

## Files:
- Attendify.exe: Main application
- start.bat: Launcher script
- data/: Contains database and uploaded files

## Requirements:
- No internet connection required
- No Python installation needed
- All dependencies are bundled

## Troubleshooting:
- If the system doesn't start, run Attendify.exe directly
- Make sure port 5000 is available
- Check if antivirus is blocking the executable

## Support:
Keep this folder intact for proper functioning.
Database and uploads are stored in the "data" folder.
'''
            
            readme_file = self.package_dir / "README.txt"
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            print("   ✓ Startup files created")
            return True
            
        except Exception as e:
            print(f"   ✗ Failed to create startup files: {e}")
            return False
    
    def build(self):
        """Main build process"""
        print("🚀 Starting Attendify Build")
        print("=" * 50)
        
        steps = [
            ("Clean previous builds", self.clean_previous_builds),
            ("Check requirements", self.check_requirements),
            ("Install dependencies", self.install_dependencies),
            ("Build executable", self.build_executable),
            ("Create portable package", self.create_portable_package),
            ("Create startup files", self.create_startup_files),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            if not step_func():
                print(f"❌ Build failed at: {step_name}")
                return False
        
        print("\n" + "=" * 50)
        print("✅ BUILD COMPLETED SUCCESSFULLY!")
        print(f"📁 Package location: {self.package_dir}")
        print("📋 Next steps:")
        print("   1. Copy the 'Attendify_Portable' folder to USB")
        print("   2. Transfer to target PC")
        print("   3. Run 'start.bat' to launch the system")
        print("=" * 50)
        
        return True

if __name__ == "__main__":
    builder = AttendifyBuilder()
    success = builder.build()
    
    if not success:
        input("\nPress Enter to exit...")
        sys.exit(1)