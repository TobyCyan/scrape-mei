"""
Build script to create a standalone executable for ScrapeMei.

This script uses PyInstaller to bundle the application into a single executable file.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


def parse_requirements():
    """Parse requirements.txt and return a list of package names."""
    requirements_file = Path('requirements.txt')
    
    if not requirements_file.exists():
        print("Warning: requirements.txt not found. Using default dependencies.")
        return []
    
    packages = []
    with open(requirements_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Extract package name (remove version specifiers)
            package = line.split('>=')[0].split('==')[0].split('<')[0].split('>')[0].strip()
            
            # Skip pyinstaller itself
            if package.lower() == 'pyinstaller':
                continue
                
            packages.append(package)
    
    return packages


def get_hidden_imports():
    """Generate list of hidden imports from requirements.txt and additional modules."""
    hidden_imports = []
    
    # Parse requirements.txt
    packages = parse_requirements()
    
    # Map package names to actual import names
    package_map = {
        'beautifulsoup4': 'bs4',
        # Add more mappings if needed
    }
    
    # Add main packages from requirements.txt
    for package in packages:
        import_name = package_map.get(package, package)
        hidden_imports.append(import_name)
        
        # Add known submodules for specific packages
        if import_name == 'lxml':
            hidden_imports.extend(['lxml.etree', 'lxml._elementpath'])
    
    # Add tkinter and its submodules (not in requirements.txt)
    hidden_imports.extend([
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.filedialog',
        'tkinter.messagebox',
    ])
    
    # Add PIL if needed (not in requirements.txt)
    if 'PIL' not in hidden_imports:
        hidden_imports.extend(['PIL', 'PIL._tkinter_finder'])
    
    # Add standard library modules that might not be auto-detected
    hidden_imports.extend(['asyncio', 'pathlib', 'logging'])
    
    return hidden_imports


def clean_build_artifacts():
    """Remove previous build artifacts."""
    print("Cleaning previous build artifacts...")
    
    artifacts = ['build', 'dist', '*.spec']
    for artifact in artifacts:
        if '*' in artifact:
            # Handle wildcard patterns
            for file in Path('.').glob(artifact):
                if file.is_file():
                    print(f"  Removing {file}")
                    file.unlink()
        else:
            path = Path(artifact)
            if path.exists():
                print(f"  Removing {path}")
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()


def build_executable(debug_mode=False):
    """Build the executable using PyInstaller."""
    print("\nBuilding executable with PyInstaller...")
    
    # Get hidden imports from requirements.txt and additional modules
    hidden_imports = get_hidden_imports()
    print(f"Hidden imports: {', '.join(hidden_imports)}")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',                    # Create a single executable
        '--name', 'ScrapeMei',          # Output executable name
        '--icon', 'NONE',               # No icon (can add one later)
        '--add-data', 'src/logic;logic', # Include logic folder
        '--noupx',                      # Disable UPX compression (can cause issues)
    ]
    
    # Add windowed only if not in debug mode
    if not debug_mode:
        cmd.append('--windowed')        # No console window (GUI app)
    else:
        print("DEBUG MODE: Building with console window for error visibility")
    
    # Add all hidden imports
    for module in hidden_imports:
        cmd.extend(['--hidden-import', module])
    
    # Add remaining options
    cmd.extend([
        '--collect-all', 'tkinter',     # Collect all tkinter files
        '--clean',                      # Clean PyInstaller cache
        'run.py'                        # Entry point script
    ])
    
    # On Windows, use semicolon for add-data separator
    if sys.platform == 'win32':
        # Already using semicolon above
        pass
    else:
        # On Unix, use colon instead
        cmd = [c.replace(';', ':') if '--add-data' in cmd[cmd.index(c)-1:cmd.index(c)+1] else c for c in cmd]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error:\n{e.stderr}")
        return False


def verify_executable():
    """Verify the executable was created successfully."""
    exe_name = 'ScrapeMei.exe' if sys.platform == 'win32' else 'ScrapeMei'
    exe_path = Path('dist') / exe_name
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n✓ Executable created successfully!")
        print(f"  Location: {exe_path.absolute()}")
        print(f"  Size: {size_mb:.2f} MB")
        return True
    else:
        print(f"\n✗ Executable not found at {exe_path}")
        return False


def main():
    """Main build process."""
    print("=" * 70)
    print("ScrapeMei - Build Executable")
    print("=" * 70)
    
    # Check for debug mode flag
    debug_mode = '--debug' in sys.argv or '-d' in sys.argv
    if debug_mode:
        print("\n⚠️  DEBUG MODE ENABLED - Console window will be visible")
    
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
    if not build_executable(debug_mode):
        print("\nBuild failed!")
        return 1
    
    # Verify result
    if not verify_executable():
        print("\nVerification failed!")
        return 1
    
    print("\n" + "=" * 70)
    print("Build completed successfully!")
    print("=" * 70)
    
    if debug_mode:
        print("\nDEBUG BUILD - Run the .exe to see error messages in console")
    else:
        print("\nNext steps:")
        print("  1. Test the executable in dist/ScrapeMei.exe")
        print("  2. Distribute the executable to users")
        print("  3. Note: Users do NOT need Python installed")
    
    print("\nTroubleshooting:")
    print("  - If you get 'failed to start python embedded interpreter':")
    print("    1. Run: python build.py --debug")
    print("    2. Launch the debug .exe to see detailed error messages")
    print("    3. Check if antivirus is blocking the .exe")
    print("    4. Try running .exe as administrator")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
