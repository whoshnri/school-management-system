import os
import sys
import subprocess
from pathlib import Path

def create_desktop_shortcut():
    """Create a desktop shortcut for the School Management System."""
    print("Setting up desktop shortcut...")
    
    # Paths
    project_dir = Path(__file__).parent.absolute()
    main_script = project_dir / "main.py"
    icon_file = project_dir / "app_icon.png"
    
    # Desktop path
    desktop = Path(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'))
    shortcut_path = desktop / "School Management System.lnk"
    
    # Python executable (use pythonw.exe to hide console)
    python_exe = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable  # Fallback to normal python if pythonw not found
    
    # PowerShell command to create shortcut
    # TargetPath: Python executable
    # Arguments: main.py
    # WorkingDirectory: project folder
    # IconLocation: path to icon
    
    ps_command = f"""
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
    $Shortcut.TargetPath = '{python_exe}'
    $Shortcut.Arguments = '"{main_script}"'
    $Shortcut.WorkingDirectory = '{project_dir}'
    if (Test-Path '{icon_file}') {{
        $Shortcut.IconLocation = '{icon_file}'
    }}
    $Shortcut.Save()
    """
    
    try:
        subprocess.run(["powershell", "-Command", ps_command], check=True)
        print(f"\nSuccess! Desktop shortcut created at:\n{shortcut_path}")
        print("\nNote: If you have a custom icon, name it 'app_icon.png' in the project folder and run this script again.")
    except Exception as e:
        print(f"\nFailed to create shortcut: {e}")

if __name__ == "__main__":
    if os.name == 'nt':
        create_desktop_shortcut()
    else:
        print("This script is designed for Windows systems.")
