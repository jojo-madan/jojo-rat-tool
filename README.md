# jojo-rat-tool
Remote Access Tool in Python - Attacker and Victim sides.
# Jojo-RAT Tool

**Remote Access Tool (RAT) built in Python**  
This project includes two components:  
- **Attacker side:** A Tkinter GUI client to control the victim machine remotely.  
- **Victim side:** A Python server script running on the target machine to execute commands and send back data.

---

## Features

- System information retrieval
- File system navigation and management
- Screenshot and webcam capture
- Clipboard access
- Wi-Fi password extraction (Windows)
- Remote shell command execution
- Lock and shutdown victim machine
- Simple and intuitive GUI for the attacker

---

## Requirements

- Python 3.x  
- Required libraries: `tkinter`, `socket`, `opencv-python`, `mss`, `clipboard`, `glob`, `re` (install via pip if needed)

---

## Setup

### Victim Side
1. Run the victim script on the target window  machine:
   ```bash
   python victim.py
The victim machine listens on port 9999 for incoming attacker connections.

Attacker Side
Run the attacker GUI script on your linux machine:

bash
Copy
Edit
python attacker.py
Enter the victim machine IP and port (default 9999), then connect.

Usage
Use the GUI tabs on the attacker client to send commands like:
Get system info
Take screenshots
Capture webcam images
Run shell commands
Browse files and directories

Files like screenshots or webcam captures are received and saved automatically.

Disclaimer
This tool is only for educational and authorized testing purposes.
Unauthorized access to computers is illegal and unethical. Use responsibly.

Author
Madan Neupane (Jojo)
BSc (Hons) Ethical and Cybersecurity
Softwarica College of IT and E-commerce
