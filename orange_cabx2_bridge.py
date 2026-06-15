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
    print("Please run: pip3 install hidapi mido --break-system-packages")
    sys.exit(1)

# Hardware footprints
MOOER_VID = 0x0483
MOOER_PID = 0x5703

def send_hid_payload(device, payload):
    """Encapsulates the raw message transfer over the HID link layer."""
    try:
        # Construct full 64-byte USB HID report framework
        report = [0x00] * 64
        for i, val in enumerate(payload):
            if i < 64:
                report[i] = val
        
        device.write(bytes(report))
        time.sleep(0.02)  # Guard window for processing cycle
        return True
    except Exception as e:
        print(f"[!] Write failure occurred over HID layer: {e}")
        return False

def process_midi_payload(msg, hid_dev):
    """Processes incoming MIDI messages and maps them to Mooer Cab X2 payloads."""
    if msg.type == 'program_change':
        pc_val = msg.program
        print(f"[*] Processing Program Change: PC {pc_val}")
        
        # Guard limits matching Mooer preset index map (0-13)
        if 0 <= pc_val <= 13:
            # Replicated control frame structure for patch deployment
            payload = [
                0x4d, 0x4f, 0x4f, 0x45, 0x52, 0x00, 0x00, 0x00,
                0x01, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00,
                0x0b, 0x00, 0x00, 0x00, pc_val, 0x00, 0x00, 0x00
            ]
            
            if send_hid_payload(hid_dev, payload):
                print(f"[+] Successfully deployed Mooer Preset Target Slot: {pc_val + 1}")
        else:
            print(f"[!] Warning: Target slot {pc_val} exceeds bounds (0-13)")

def run_midi_listener():
    """Main lifecycle thread monitoring incoming MIDI signals from the controller."""
    print("============================================================")
    print("ORANGE PI / MIDI CAPTAIN BACKEND BRIDGE RUNTIME ACTIVE")
    print("============================================================")
    
    # Initialize connection to Mooer hardware over USB HID node
    try:
        hid_dev = hid.device()
        hid_dev.open(MOOER_VID, MOOER_PID)
        print("[+] Established direct link layer with Mooer Cab X2 device footprint.")
    except Exception as e:
        print(f"[!] Critical Error: Unable to open Mooer Cab X2 via HID. Details: {e}")
        print("    Check your udev rules (/etc/rules.d/99-mooer.rules) and USB connection.")
        sys.exit(1)
        
    try:
        # Explicitly pass api='LINUX_ALSA' to prevent falling back to JACK server
        available_ports = mido.get_input_names(api='LINUX_ALSA')
        print(f"Detected System MIDI Ports: {available_ports}")
        
        target_port = None
        for port in available_ports:
            if "captain" in port.lower() or "midi" in port.lower():
                target_port = port
                break
                
        if not target_port:
            print("[!] Error: No available USB MIDI Devices identified on your Orange Pi system ports.")
            print("    Please connect the MIDI Captain hardware footprint via its USB connection link.")
            hid_dev.close()
            sys.exit(1)
            
        print(f"[+] Initializing connection stream targeting port node: [{target_port}]")
        
        # Explicitly bind the incoming connection hook to the ALSA engine framework
        with mido.open_input(target_port, api='LINUX_ALSA') as inport:
            print("[+] Channel communication streaming open. Listening for live input messages...")
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
