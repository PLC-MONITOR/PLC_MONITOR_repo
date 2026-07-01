# PLC Manager — Flask + Snap7 for Raspberry Pi 4

Siemens PLC monitoring and control app using Snap7 and Flask.
Runs on Raspberry Pi 4, accessible from any browser on the local network.

---

## Install

### 1. Install system dependencies

```bash
sudo apt-get update
sudo apt-get install -y libsnap7-1 libsnap7-dev python3-pip
```

### 2. Install Python packages

```bash
cd plc_manager
pip3 install -r requirements.txt
```

> If pip install of python-snap7 fails, try:
> ```bash
> pip3 install python-snap7 --break-system-packages
> ```

### 3. Run

```bash
python3 app.py
```

Access at: `http://<raspberry-pi-ip>:5000`

---

## Run as a systemd service (auto-start on boot)

Create `/etc/systemd/system/plcmanager.service`:

```ini
[Unit]
Description=PLC Manager Flask App
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/plc_manager
ExecStart=/usr/bin/python3 /home/pi/plc_manager/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable plcmanager
sudo systemctl start plcmanager
```

---

## Snap7 without the library installed

If `snap7` is not installed, the app still runs — all PLC operations will return
an error message `"snap7 not installed"`. Configuration (adding PLCs and
variables) works fully without Snap7.

---

## Page 1 — Configuration

- Set the process name
- Add PLCs: name, IP, rack, slot
- Test connectivity per PLC
- Add variables per PLC:
  - Memory area: DB, M, I, Q, T, C
  - DB number (only for DB area)
  - Data type: BOOL, BYTE, INT, DINT, WORD, DWORD, REAL
  - Start byte
  - Bit number (only for BOOL)

## Page 2 — Live Monitor

- Auto-polls all PLCs at configurable interval (1s, 2s, 5s, 10s)
- Shows live values for all variables
- BOOL variables: click toggle to write TRUE/FALSE
- Numeric variables: type value and click Write
- Changed values flash green on update
- Per-PLC manual read button

---

## Supported Siemens PLCs

All S7 PLCs supported by Snap7:
- S7-300, S7-400
- S7-1200, S7-1500 (with PUT/GET enabled)
- S7-200 via CP243 or CP343

For S7-1200/1500: enable "Permit access with PUT/GET" in TIA Portal
under PLC Properties → Protection & Security.
