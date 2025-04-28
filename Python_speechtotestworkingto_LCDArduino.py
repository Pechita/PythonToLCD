import speech_recognition as sr
import serial
import time

# Setup serial connection
ser = serial.Serial('COM4', 9600)
time.sleep(2)

# Setup recognizer and mic
r = sr.Recognizer()
r.energy_threshold = 300  # Sensitivity to sound level (you can adjust if needed)
r.pause_threshold = 1.5   # 🔥 How long a pause means "you're done talking" (1.5 sec)

mic = sr.Microphone()

listening = False

# Send "Waiting for Hey World" at start
ser.write(b"Waiting for\nHey World\n")
print('System Ready.')
print('Waiting for "Hey World"...')

with mic as source:
    r.adjust_for_ambient_noise(source)

    while True:
        if not listening:
            print('Listening for "Hey World"...')
            ser.write(b"Waiting for\nHey World\n")
            # Wait without any timeout

        # ✨ Now it will wait as long as needed to finish talking naturally
        audio = r.listen(source)  # NO timeout, NO phrase time limit!

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

                # Split words for pagination
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

                    # Send two lines to LCD
                    message = line1 + "\n" + line2 + "\n"
                    ser.write(message.encode())
                    print(f"Sent to LCD:\n{line1}\n{line2}")
                    time.sleep(2)

        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

ser.close()
print("Serial connection closed.")
