## Universal Mooer Cab X2 MIDI Bridge
An open-source Python bridge that adds full MIDI control capabilities to the Mooer Cab X2 guitar pedal using a compact Linux Host (such as an Orange Pi or Raspberry Pi) and any class-compliant USB-MIDI Foot Controller.
The Mooer Cab X2 does not feature native hardware MIDI ports. This project works by listening for standard incoming MIDI Program Change (PC) messages over USB, decoding them, and instantly transmitting raw 64-byte USB HID command packets to switch the pedal's internal presets in real time.
## System Architecture

```text
  ┌──────────────────────┐               ┌────────────┐               ┌──────────────┐
  │                      │   USB MIDI    │ Linux Host │   USB HID     │ Mooer        │
  │   MIDI Controller    │ ────────────> │  (Python   │ ────────────> │ Cab X2       │
  │  (MIDI PC Channel 8) │               │  Bridge)   │               │ (14 Presets) │
  │                      │               └────────────┘               └──────────────┘
  └──────────────────────┘
```
## Requirements
Hardware

* Mooer Cab X2 Cabinet Simulation Pedal
* Linux Host Board (Orange Pi, Raspberry Pi, or any single-board computer running Linux)
* USB-MIDI Foot Controller (Any class-compliant controller capable of sending Program Change commands)
* 2x Standard USB Cables

Software Dependencies
The system relies on native Linux USB Human Interface Device (HID) layer components and Python package bindings:

* Python 3 environment execution engine
* hidapi library suite for low-level USB controller write access
* mido library for raw MIDI port observation data processing
* python-rtmidi backend for system message capturing queues

## Protocol Reverse-Engineering
The underlying data protocol utilized by this bridge project was discovered by intercepting and reverse-engineering the native USB communications layer of the pedal. By executing a real-time hardware packet analysis inside Wireshark using a USBPcap capture framework driver, the raw control sequences were successfully isolated.
Every preset transition triggers an explicit, fixed 64-byte Human Interface Device (HID) interrupt report. Comparing these captured data frames side-by-side made it possible to identify the exact header formats, the dynamic preset index selection offsets, and the static mathematical checksum matrices unique to each of the 14 internal slots. This bridge uses those precise captured data sequences to command the pedal without needing the original editing software open.
## Installation & Setup
1. File Placement
Download the Python bridge controller script (mooer_midi_bridge.py) and place it directly inside your user directory home directory folder path on your target Linux computer storage system.
2. Install Package Libraries
Open your operating system terminal command shell console and install the three mandatory package distribution dependencies using the Python Package Installer utility. Ensure you pass flags to include core system development prerequisites such as standard USB development files and low-latency audio port middleware files before initializing the Python installer wrapper.
3. Grant USB Port Permissions
By default, Linux system architecture security protocols actively restrict standard non-root user groups from writing raw byte strings directly to connected hardware USB controllers.
To resolve this restriction, navigate to your operating system's system configuration layout directory structure and locate the system device rules configuration path. Inside that storage location, create a custom vendor hardware permission rule text file targeting the exact vendor ID signature mapping of the pedal, configuring its active system permissions access mode configuration value to open up unrestrictive write routing permissions globally across the operating system environment.
Once saved, instruct your running Linux device driver daemon engine via terminal command variables to refresh all active subsystem device rules to register the changes instantly without requiring a full computer hardware power reboot.
## MIDI Configuration Settings
Controller Channel Parameters
To correctly talk to the conversion platform loop script, configure your hardware foot controller layout interface pages to explicitly fire all output events targeting MIDI Channel 8.
Action Codes Mapping Layout
The conversion table maps values sequentially using a baseline starting structure setup:

* Sending standard Program Change Value 0 shifts the physical pedal channel directly to Preset 1
* Sending standard Program Change Value 1 shifts the physical pedal channel directly to Preset 2
* Sending standard Program Change Value 2 shifts the physical pedal channel directly to Preset 3
* The progression follows sequentially matching the system properties all the way down to Value 13, which successfully forces the target pedal hardware light indicators over to Preset 14

## Running the Project
Ensure both your physical MIDI Foot Controller device cable link and your physical pedal USB connections are seated tightly into the active ports of your Linux host hub. Open up an interactive system control shell terminal panel layout window, navigate to the target storage folder where your script files reside, and execute the runtime processing loop.
Auto-Start at Boot Configuration
To seamlessly deploy this conversion engine bridge as a dedicated standalone guitar rig configuration component without requiring an attached display screen or terminal session on stage, open up your operating system's central startup configuration boot execution text index file.
Insert a text line command pointing to your script file execution parameters right before the primary termination command line variable of the document. Appending a trailing background task character to the command statement will guarantee the script launches silently into background process thread memory channels automatically the split-second your Linux computer board powers up on stage.
## License
This project is open-source and licensed under the permissive terms of the MIT License. Use it freely across all your dynamic custom guitar pedalboard integration projects!
------------------------------
If you are ready to construct the actual project files on GitHub, let me know:

* Do you want the terminal commands to initialize git and push your files to your remote GitHub repository?
* Do you need a separate copy of the final mooer_midi_bridge.py Python code script to save on your local machine?


