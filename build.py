# يبني البرنامج (exe) ثم ملف التثبيت (Setup.exe). شغّله بالضغط على build.bat
import os
import re
import shutil
import subprocess
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
version = re.search(r'APP_VERSION\s*=\s*"([^"]+)"', open("adhan_app.py", encoding="utf-8").read()).group(1)
print(f"=== Building Adhan App v{version} ===")


def run(cmd):
    print(">", " ".join(cmd))
    subprocess.check_call(cmd)


if not os.path.exists("wall.png"):
    print("\n*** WARNING: wall.png was not found next to build.py - the app will use a plain gradient background.")
    print("*** Put wall.png here and run build.bat again if you want your background image.\n")
for folder in ("adhan", "takbeer"):
    if not os.path.isdir(folder) or not os.listdir(folder):
        print(f"*** NOTE: folder '{folder}' is empty or missing - no audio files will be bundled.")

print("\n[1/3] Installing requirements...")
run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "pyinstaller"])

print("\n[2/3] Building the app with PyInstaller...")
run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--windowed", "--name", "AdhanApp",
     "--icon", "icon.ico", "--add-data", "icon.ico;.", "--collect-all", "customtkinter",
     "--collect-data", "tzdata", "--hidden-import", "pystray._win32", "adhan_app.py"])

print("\n[3/3] Building the installer with Inno Setup...")
import make_wizard_images
make_wizard_images.main()
candidates = [
    os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Inno Setup 6", "ISCC.exe"),
    os.path.join(os.environ.get("ProgramFiles", ""), "Inno Setup 6", "ISCC.exe"),
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Inno Setup 6", "ISCC.exe"),
    shutil.which("ISCC") or "",
]
iscc = next((c for c in candidates if c and os.path.exists(c)), None)
if not iscc:
    print("\nInno Setup was not found. Install it (free) from https://jrsoftware.org/isdl.php")
    print("then run build.bat again.")
    sys.exit(1)
run([iscc, f"/DMyAppVersion={version}", "installer.iss"])

print(f"\nDONE!  Your installer: installer_output\\AdhanApp-Setup-{version}.exe")
