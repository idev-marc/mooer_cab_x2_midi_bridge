#!/bin/bash
# ============================================================
# Mooer Cab X2 MIDI Bridge — Auto Installer
# Orange Pi Zero 3 / Debian-based systems
# ============================================================

set -e

INSTALL_DIR="/opt/mooer-bridge"
SERVICE_USER="root"
SCRIPT_URL="https://raw.githubusercontent.com/idev-marc/mooer_cab_x2_midi_bridge/main/orange_cabx2_bridge.py"

echo "============================================================"
echo " Mooer Cab X2 MIDI Bridge Installer"
echo "============================================================"

# ------------------------------------------------------------
# 1. System dependencies
# ------------------------------------------------------------
echo "[1/6] Installing system dependencies..."
sudo apt update -qq
sudo apt install -y \
    python3 python3-pip python3-venv \
    libhidapi-hidraw0 libhidapi-dev gcc \
    alsa-utils libudev-dev curl

# ------------------------------------------------------------
# 2. Create install directory and download script
# ------------------------------------------------------------
echo "[2/6] Setting up install directory at $INSTALL_DIR..."
sudo mkdir -p "$INSTALL_DIR"
sudo chown "$USER:$USER" "$INSTALL_DIR"

echo "      Downloading bridge script..."
curl -fsSL "$SCRIPT_URL" -o "$INSTALL_DIR/orange_cabx2_bridge.py"

# Write requirements.txt
cat > "$INSTALL_DIR/requirements.txt" <<'EOF'
hidapi>=0.14.0
mido>=1.3.0
python-rtmidi>=1.5.0
EOF

# ------------------------------------------------------------
# 3. Python virtual environment
# ------------------------------------------------------------
echo "[3/6] Creating Python virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --quiet --upgrade pip
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

# ------------------------------------------------------------
# 4. udev rule
# ------------------------------------------------------------
echo "[4/6] Installing udev rule for Mooer Cab X2 (0483:5703)..."
sudo tee /etc/udev/rules.d/99-mooer-cab-x2.rules > /dev/null <<'EOF'
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5703", MODE="0660", GROUP="plugdev"
EOF

sudo usermod -aG plugdev "$USER"
sudo udevadm control --reload-rules
sudo udevadm trigger

echo "      >>> Unplug and replug the Mooer USB cable now if already connected <<<"

# ------------------------------------------------------------
# 5. systemd service
# ------------------------------------------------------------
echo "[5/6] Installing systemd service..."
sudo tee /etc/systemd/system/mooer-bridge.service > /dev/null <<EOF
[Unit]
Description=Mooer Cab X2 MIDI Bridge
After=sound.target local-fs.target
Wants=sound.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/orange_cabx2_bridge.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable mooer-bridge
sudo systemctl start mooer-bridge

# ------------------------------------------------------------
# 6. SD card corruption protection
# ------------------------------------------------------------
echo "[6/6] Configuring SD card protection..."

# sync-on-halt service
sudo tee /etc/systemd/system/sync-on-halt.service > /dev/null <<'EOF'
[Unit]
Description=Sync filesystems before halt
DefaultDependencies=no
Before=shutdown.target reboot.target halt.target
Requires=local-fs.target

[Service]
Type=oneshot
ExecStart=/bin/sync
TimeoutSec=30

[Install]
WantedBy=halt.target reboot.target shutdown.target
EOF

sudo systemctl enable sync-on-halt

# Add tmpfs mounts if not already present
if ! grep -q "tmpfs /tmp" /etc/fstab; then
    echo "tmpfs  /tmp      tmpfs  defaults,nosuid,nodev,size=64M  0  0" | sudo tee -a /etc/fstab > /dev/null
    echo "      Added tmpfs /tmp"
fi
if ! grep -q "tmpfs /var/log" /etc/fstab; then
    echo "tmpfs  /var/log  tmpfs  defaults,nosuid,nodev,size=32M  0  0" | sudo tee -a /etc/fstab > /dev/null
    echo "      Added tmpfs /var/log"
fi

# ------------------------------------------------------------
# Done
# ------------------------------------------------------------
echo ""
echo "============================================================"
echo " Installation complete!"
echo "============================================================"
echo ""
echo " Service status:"
sudo systemctl status mooer-bridge --no-pager -l
echo ""
echo " Useful commands:"
echo "   journalctl -fu mooer-bridge     # live logs"
echo "   sudo systemctl restart mooer-bridge"
echo "   ls -la /dev/hidraw*             # check HID permissions"
echo "   lsusb                           # check USB devices"
echo ""
echo " NOTE: If you see 'open failed' in the logs, make sure"
echo "       the Mooer is plugged in AFTER the udev rules loaded."
echo "       Unplug and replug the Mooer USB cable, then:"
echo "       sudo systemctl restart mooer-bridge"
