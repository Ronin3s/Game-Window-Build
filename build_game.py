import PyInstaller.__main__
import os
import sys
import shutil

def build():
    # Determine separator based on OS
    # Windows uses ';', Linux/Unix uses ':'
    separator = ';' if os.name == 'nt' else ':'
    
    print(f"Detected OS: {os.name}")
    print(f"Using separator: '{separator}'")
    
    # Define build arguments
    args = [
        'main.py',
        '--name=TransportationGame',
        '--onefile',
        '--windowed',
        '--noconfirm',
        f'--add-data=assets{separator}assets',
    ]
    
    # Add icon if it exists
    if os.path.exists('assets/images/car.png'):
        args.append('--icon=assets/images/car.png')
    
    print("Starting build with arguments:", args)
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\nBuild complete!")
    print(f"Check the 'dist' folder for your executable.")
    
    if os.name != 'nt':
        print("\nNOTE: You built this on Linux/Mac. The output file is a Linux/Mac executable.")
        print("To get a Windows .exe, you MUST run this script on a Windows machine.")

if __name__ == "__main__":
    build()
