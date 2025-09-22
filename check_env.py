import sys
import os

print("--- Python Interpreter Info ---")
print(f"Executable: {sys.executable}")
print(f"Version: {sys.version}")

print("\n--- Module Search Paths (sys.path) ---")
for i, path in enumerate(sys.path):
    print(f"{i}: {path}")

print("\n--- Checking for psutil in site-packages ---")
venv_path = os.path.dirname(os.path.dirname(sys.executable))
site_packages_path = os.path.join(venv_path, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')

print(f"Expected site-packages path: {site_packages_path}")
if os.path.exists(site_packages_path):
    print("Site-packages directory EXISTS.")
    psutil_dir = os.path.join(site_packages_path, 'psutil')
    if os.path.exists(psutil_dir):
        print("psutil directory FOUND inside site-packages.")
    else:
        print("psutil directory NOT FOUND inside site-packages.")
        print("Listing contents of site-packages:")
        try:
            print(os.listdir(site_packages_path))
        except Exception as e:
            print(f"Could not list directory: {e}")
else:
    print("Site-packages directory DOES NOT EXIST.")
