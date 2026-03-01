"""
Alternative build script that creates a folder distribution instead of a single .exe.
This can help diagnose issues and may work better on some systems.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

# Import functions from build.py
sys.path.insert(0, str(Path(__file__).parent))
from build import parse_requirements, get_hidden_imports, clean_build_artifacts


def build_folder_executable():
    """Build the executable as a folder distribution (not --onefile)."""
    print("\nBuilding folder distribution with PyInstaller...")
    
    # Get hidden imports from requirements.txt and additional modules
    hidden_imports = get_hidden_imports()
    print(f"Hidden imports: {', '.join(hidden_imports)}")
    
    # PyInstaller command WITHOUT --onefile
    cmd = [
        'pyinstaller',
        # NO --onefile flag here
        '--name', 'ScrapeMei',          # Output executable name
        '--icon', 'NONE',               # No icon (can add one later)
        '--add-data', 'src/logic;logic', # Include logic folder
        '--noupx',                      # Disable UPX compression
        '--windowed',                   # No console window
    ]
    
    # Add all hidden imports
    for module in hidden_imports:
        cmd.extend(['--hidden-import', module])
    
    # Add remaining options
    cmd.extend([
        '--collect-all', 'tkinter',     # Collect all tkinter files
        '--clean',                      # Clean PyInstaller cache
        'run.py'                        # Entry point script
    ])
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error:\n{e.stderr}")
        return False


def verify_folder_executable():
    """Verify the folder executable was created successfully."""
    exe_path = Path('dist/ScrapeMei/ScrapeMei.exe')
    
    if exe_path.exists():
        # Calculate total folder size
        total_size = sum(f.stat().st_size for f in Path('dist/ScrapeMei').rglob('*') if f.is_file())
        size_mb = total_size / (1024 * 1024)
        
        print(f"\n✓ Folder distribution created successfully!")
        print(f"  Location: {exe_path.parent.absolute()}")
        print(f"  Total size: {size_mb:.2f} MB")
        print(f"  Executable: {exe_path}")
        print(f"\n  To distribute: Zip the entire 'dist/ScrapeMei' folder")
        return True
    else:
        print(f"\n✗ Executable not found at {exe_path}")
        return False


def main():
    """Main build process."""
    print("=" * 70)
    print("ScrapeMei - Build Folder Distribution")
    print("=" * 70)
    print("\nThis creates a folder with the .exe and required files.")
    print("Distributing the entire folder may avoid some runtime errors.\n")
    
    # Check if PyInstaller is installed
    try:
        subprocess.run(['pyinstaller', '--version'], 
                      check=True, 
                      capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: PyInstaller is not installed.")
        print("Install it with: pip install pyinstaller")
        return 1
    
    # Clean previous builds
    clean_build_artifacts()
    
    # Build executable
    if not build_folder_executable():
        print("\nBuild failed!")
        return 1
    
    # Verify result
    if not verify_folder_executable():
        print("\nVerification failed!")
        return 1
    
    print("\n" + "=" * 70)
    print("Build completed successfully!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Test: dist/ScrapeMei/ScrapeMei.exe")
    print("  2. Distribute the entire 'dist/ScrapeMei' folder as a .zip")
    print("  3. Users extract the .zip and run ScrapeMei.exe")
    print("  4. Note: Users do NOT need Python installed")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
