#!/usr/bin/env python3
import os
import sys
import time

# Force rtmidi to use the lightweight ALSA backend instead of JACK
os.environ["RTMIDI_API"] = "LINUX_ALSA"
os.environ["MIDO_BACKEND"] = "mido.backends.rtmidi"

try:
    import hid
    import mido
except ImportError as e:
    print(f"[!] Dependency Missing: {e}")
    sys.exit(1)

# Mooer Hardware USB HID Signatures
MOOER_VID = 0x0483
MOOER_PID = 0x5703

# Target configuration
TARGET_CHANNEL = 7  # 7 in code maps directly to physical MIDI Channel 8

# Custom Hardware Preset Byte Mapping Profile
PRESET_MAP = {
    0:  [0x09, 0xAA, 0x55, 0x03, 0x00, 0x91, 0x00, 0x01, 0x4E, 0x05], # Preset 1
    1:  [0x09, 0xAA, 0x55, 0x03, 0x00, 0x91, 0x01, 0x01, 0x7D, 0x34], # Preset 2
    2:  [0x09, 0xAA, 0x55, 0x03, 0x00, 0x91, 0x02, 0x01, 0x28, 0x67], # Preset 3
    3:  [0x09, 0xAA, 0x55, 0x03, 0x00, 0x91, 0x03, 0x01, 0x1B, 0x56], # Preset 4
    4:  [0x09, 0xAA, 0x55, 0x03, 0x00, 0x91, 0x04, 0x01, 0x82, 0xC1], # Preset 5
    5:  [0x09, 0xAA, 0x55, 0x03, 0x00, 0x91, 0x05, 0x01, 0xB1, 0xF0], # Preset 6
    6:  [0x09, 0xAA, 0x55, 0x03, 0x00, 0x91, 0x06, 0x01, 0xE4, 0xA3], # Preset 7
    7:  [0x09, 0xAA, 0x55, 0x03, 0x00, 0x91, 0x07, 0x01, 0xD7, 0x92], # Preset 8
    8:  [0x09, 0xAA, 0x55, 0x03, 0x00, 0x91, 0x08, 0x01, 0xC7, 0xAC], # Preset 9
    9:  [0x09, 0xAA, 0x55, 0x03, 0x00, 0x91, 0x09, 0x01, 0xF4, 0x9D], # Preset 10
    10: [0x09, 0xAA, 0x55, 0x03, 0x00, 0x91, 0x0A, 0x01, 0xA5, 0xCE], # Preset 11
    11: [0x09, 0xAA, 0x55, 0x03, 0x00, 0x91, 0x0B, 0x01, 0x92, 0xFF], # Preset 12
    12: [0x09, 0xAA, 0x55, 0x03, 0x00, 0x91, 0x0C, 0x01, 0x0B, 0x68], # Preset 13
    13: [0x09, 0xAA, 0x55, 0x03, 0x00, 0x91, 0x0D, 0x01, 0x38, 0x59], # Preset 14
}

def send_hid_payload(device, payload):
    """Constructs a strict 64-byte output report framework and pushes to the HID layer."""
    try:
        # Crucial for Linux HIDAPI: The first byte must be the Report ID (0x00)
        report = [0x00] * 65  
        
        # Populate the custom 10-byte sequence starting right after the Report ID byte
        for i, val in enumerate(payload):
            if i < 64:
                report[i + 1] = val
                
        device.write(bytes(report))
        time.sleep(0.02)  # Hardware processing guard window
        return True
    except Exception as e:
        print(f"[!] Direct HID write frame error: {e}")
        return False

def process_midi_payload(msg, hid_dev):
    """Processes incoming MIDI messages and maps them to Mooer Cab X2 payloads."""
    if msg.type == 'program_change' and msg.channel == TARGET_CHANNEL:
        # Adjust incoming hardware message value down by 1 to fix the 1-to-1 mapping offset
        target_preset_index = msg.program - 1
        display_pc = msg.program  # Keeps original PC number for the console log
        
        print(f"[*] Processing Program Change (Ch 8): PC {display_pc}")
        
        # Fetch the payload from your updated map profile matrix using the adjusted index
        if target_preset_index in PRESET_MAP:
            payload = PRESET_MAP[target_preset_index]
            if send_hid_payload(hid_dev, payload):
                print(f"[+] Successfully deployed Custom Mooer Payload for Preset: {target_preset_index + 1}")
        else:
            print(f"[!] Warning: Received PC {display_pc}. Mapped index {target_preset_index} outside bounds (PC 1 - PC 14)")

def run_midi_listener():
    """Main lifecycle thread monitoring incoming MIDI signals from the controller."""
    print("============================================================")
    print("ORANGE PI / MIDI BRIDGE RUNTIME ACTIVE (CORRECTED MAP)")
    print("============================================================")
    
    # Initialize connection to Mooer hardware over USB HID node
    try:
        hid_dev = hid.device()
        hid_dev.open(MOOER_VID, MOOER_PID)
        try:
            hid_dev.set_nonblocking(1)
        except:
            pass
        print("[+] Established direct link layer with Mooer Cab X2 device footprint.")
    except Exception as e:
        print(f"[!] Critical Error: Unable to open Mooer Cab X2 via HID. Details: {e}")
        print("    Check your udev rules (/etc/rules.d) and USB connection.")
        sys.exit(1)
        
    try:
        # Fetch active ports bound to ALSA
        available_ports = mido.get_input_names(api='LINUX_ALSA')
        print(f"Detected System MIDI Ports: {available_ports}")
        
        target_port = None
        for port in available_ports:
            if any(sig in port.lower() for sig in ["captain", "midi", "ch345", "gt-1000", "pico"]):
                target_port = port
                break
                
        if not target_port:
            print("[!] Error: No available USB MIDI Devices identified on your Orange Pi system ports.")
            hid_dev.close()
            sys.exit(1)
            
        print(f"[+] Initializing continuous event listener thread loop on: '{target_port}'...")
        
        with mido.open_input(target_port, api='LINUX_ALSA') as inport:
            print("[+] Channel communication streaming open. Listening strictly on MIDI Channel 8...")
            for msg in inport:
                process_midi_payload(msg, hid_dev)
                
    except KeyboardInterrupt:
        print("\n[*] Script runtime stopped via keyboard signal. Cleaning connections.")
    except Exception as e:
        print(f"[!] Critical execution error within system pipeline: {e}")
    finally:
        try:
            hid_dev.close()
            print("[+] Connection strings cleared cleanly. System teardown complete.")
        except:
            pass

if __name__ == "__main__":
    run_midi_listener()
