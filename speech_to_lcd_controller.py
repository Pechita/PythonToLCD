
# Speech to LCD Controller
# Captures voice, waits for "Hey World" to start, "Peace World" to stop.
# Displays speech in 16x2 LCD through Arduino Serial.

import speech_recognition as sr
import serial
import time

ser = serial.Serial('COM4', 9600)
time.sleep(2)

r = sr.Recognizer()
r.energy_threshold = 300
r.pause_threshold = 1.5

mic = sr.Microphone()

listening = False

ser.write(b"Waiting for\nHey World\n")
print('System Ready.')
print('Waiting for "Hey World"...')

with mic as source:
    r.adjust_for_ambient_noise(source)

    while True:
        if not listening:
            print('Listening for "Hey World"...')
            ser.write(b"Waiting for\nHey World\n")

        audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            text = text.strip()
            print(f"Recognized: {text}")

            if not listening:
                if "hey world" in text.lower():
                    listening = True
                    print("🔵 Started Recording...")
                    ser.write(b"Recording...\n\n")
                    time.sleep(0.5)
                continue

            if listening:
                if "peace world" in text.lower():
                    listening = False
                    print("🛑 Paused Recording...")
                    ser.write(b"Waiting for\nHey World\n")
                    continue

                words = text.split()
                word_index = 0
                total_words = len(words)

                while word_index < total_words:
                    line1 = ""
                    line2 = ""
                    current_line = 1

                    while word_index < total_words:
                        word = words[word_index]

                        if len(word) > 16:
                            part1 = word[:16]
                            part2 = word[16:]
                            if current_line == 1:
                                line1 = part1
                                words[word_index] = part2
                                current_line = 2
                            else:
                                line2 = part1
                                words[word_index] = part2
                                word_index -= 1
                            break

                        if current_line == 1:
                            if len(line1) + len(word) + (1 if line1 else 0) <= 16:
                                line1 += (" " if line1 else "") + word
                                word_index += 1
                            else:
                                current_line = 2
                        elif current_line == 2:
                            if len(line2) + len(word) + (1 if line2 else 0) <= 16:
                                line2 += (" " if line2 else "") + word
                                word_index += 1
                            else:
                                break

                    message = line1 + "\n" + line2 + "\n"
                    ser.write(message.encode())
                    print(f"Sent to LCD:\n{line1}\n{line2}")
                    time.sleep(1.5)

        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

ser.close()
print("Serial connection closed.")
