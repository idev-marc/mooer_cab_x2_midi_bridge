import sys
import hid
import mido

# ==============================================================================
# 1. HARDWARE IDENTIFIERS
# Ensure these match the exact Hex IDs found during your discovery scans
# ==============================================================================
MOOER_VID = 0x0483  
MOOER_PID = 0x5703  

# ==============================================================================
# 2. CAPTURED WIRESHARK LOOKUP MATRIX
# Maps the incoming MIDI Captain PC signal values cleanly to the target outputs
# ==============================================================================
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

def send_hid_preset(midi_pc_value):
    """Formats array blocks into exact 64-byte structural layouts for Linux execution."""
    if midi_pc_value not in PRESET_MAP:
        print(f"[-] Received out-of-range MIDI code ({midi_pc_value}). Ignoring.")
        return

    try:
        # Instantiation device path over system bus
        pedal = hid.device()
        pedal.open(MOOER_VID, MOOER_PID)
        
        # Clone structural base array list elements
        payload = list(PRESET_MAP[midi_pc_value])
        
        # LINUX CONSTRAINT: Pad trailing bounds out to exactly 64 items total
        linux_size_limit = 64
        payload += [0x00] * (linux_size_limit - len(payload))
        
        # Pass stream packet array directly to device
        pedal.write(payload)
        print(f"[+] Executed Event: Mooer Cab X2 shifted to Preset {midi_pc_value + 1}!")
        
        pedal.close()
    except Exception as e:
        print(f"[!] System pipeline error attempting write command execution: {e}")

def run_midi_listener():
    print("=" * 60)
    print("ORANGE PI / MIDI CAPTAIN BACKEND BRIDGE RUNTIME ACTIVE")
    print("=" * 60)
    
    # Poll system controllers available to the python script engine instance
    available_ports = mido.get_input_names()
    print(f"Detected System MIDI Ports: {available_ports}")
    
    # Automatically locate the MIDI Captain matching string token context
    captain_port_name = None
    for port in available_ports:
        if "captain" in port.lower() or "usb midi" in port.lower():
            captain_port_name = port
            break
            
    # Default failback loop selector if explicitly missing named parameters
    if not captain_port_name:
        if available_ports:
            captain_port_name = available_ports[0]
            print(f"[!] Target signature match missed. Defaulting listeners to: '{captain_port_name}'")
        else:
            print("[!] Error: No available USB MIDI Devices identified on your Orange Pi system ports.")
            print("💡 Please connect the MIDI Captain hardware footprint via its USB connection link.")
            sys.exit(1)
            
    print(f"[+] Initializing continuous event listener thread loop on: '{captain_port_name}'...")
    
    try:
        with mido.open_input(captain_port_name) as input_stream_bus:
            print("[+] Connection online. Press foot controller switches to cycle presets.")
            for incoming_msg in input_stream_bus:
                # Capture standard Program Change statements fired from foot toggles
                if incoming_msg.type == 'program_change' and incoming_msg.channel == 11:
                    pc_signal = incoming_msg.program  # Typically zero-indexed bounds from 0-127
                    print(f"-> Signal Received! MIDI PC: {pc_signal}")
                    send_hid_preset(pc_signal)
                    
    except KeyboardInterrupt:
        print("\n[-] Operational termination loop routine completed. Closing thread connections.")

if __name__ == "__main__":
    run_midi_listener()
