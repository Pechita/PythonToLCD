# Voice to LCD System

This project allows real-time voice-controlled text display on a 16x2 LCD using Python and Arduino.

You speak naturally into your computer's microphone, and your speech is captured, processed, and sent to the LCD through an Arduino microcontroller.  
It waits for a special keyword ("Hey World") to start listening, and stops when you say ("Peace World").

---

## 🛠 How It Works

- **Python Program** (`speech_to_lcd_controller.py`) listens to your speech using SpeechRecognition.
- After you say "Hey World", the program begins capturing your spoken sentences.
- The full captured text is broken into lines that fit a 16x2 LCD.
- The Arduino (`lcd_serial_display_handler.ino`) receives this text over Serial and displays it cleanly on the LCD, paginating long messages.
- Saying "Peace World" pauses the system.

---

## 📂 Files Included

- `speech_to_lcd_controller.py` – Python script for real-time voice capture and serial transmission.
- `lcd_serial_display_handler.ino` – Arduino sketch for receiving serial data and displaying it on the LCD.
- `lcd_to_arduino_pin_diagram.txt` – Simple wiring diagram showing how to connect the LCD to Arduino.
- `Voice_to_LCD_System.zip` – Bundle containing all files.

---

## 🔧 Setup Instructions

1. **Hardware Needed:**
   - Arduino Uno (or compatible)
   - 16x2 LCD module
   - Jumper wires
   - (Optional) Potentiometer for LCD contrast adjustment

2. **Software Needed:**
   - Python 3.x
   - Python libraries:
     - `speechrecognition`
     - `pyserial`
     - `pyaudio`
   - Arduino IDE

3. **Steps:**
   - Upload `lcd_serial_display_handler.ino` to your Arduino using Arduino IDE. (MAKE SURE TO ADJUST COM TO WHATEVER COM YOU ARE USING)
   - Connect your LCD to the Arduino according to the wiring diagram.
   - Run `speech_to_lcd_controller.py` on your computer.
   - Speak into the microphone — say "**Hey World**" to start recording, "**Peace World**" to pause.

---

## 🔌 LCD to Arduino Wiring

| LCD Pin | Arduino Pin |
|:--------|:------------|
| VSS     | GND |
| VDD     | 5V |
| VO      | GND (or potentiometer center) |(You can add a resistor to your liking instead)
| RS      | D12 |
| RW      | GND |
| E       | D11 |
| D4      | D5 |
| D5      | D4 |
| D6      | D3 |
| D7      | D2 |
| A (LED+) | 5V |
| K (LED-) | GND |

---

## ⚡ Notes

- Adjust `r.energy_threshold` and `r.pause_threshold` inside the Python script if your microphone behaves differently.
- LCD contrast may need tuning if your characters are hard to read.

---
