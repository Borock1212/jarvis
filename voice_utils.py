import speech_recognition as sr
import pyttsx3
import tkinter as tk

# === Text-to-Speech (TTS) engine initialization ===
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 170)  # Set speech rate

# === Voice input function ===
def get_voice_command(output_box):
    recognizer = sr.Recognizer()
    output = []
    output_text = "\n".join(output)
    output_box.insert(tk.END, f"{output_text}\n")

    # Adjust microphone index if needed (device_index=4 might be specific)
    with sr.Microphone(device_index=4) as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        output_box.insert(tk.END, "Listening...\n")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            output_box.insert(tk.END, "Audio recorded\n")
        except sr.WaitTimeoutError:
            output_box.insert(tk.END, "Timeout reached\n")
            return "Failed to detect voice"

    try:
        # Recognize speech using Google Speech Recognition
        text = recognizer.recognize_google(audio, language="en-US")
        output_box.insert(tk.END, f"You said: {text}\n")
        # Activate command only if keyword 'Yuki' is detected
        if "yuki" in text.lower():
            command = text.lower().split("yuki", 1)[-1].strip()
            output_box.insert(tk.END, f"Activated by keyword. Command: {command}\n")
            return command
        else:
            output_box.insert(tk.END, "Keyword 'Yuki' not detected. Command ignored.\n")
            return ""
    except sr.UnknownValueError:
        output_box.insert(tk.END, "⚠️ Speech not recognized.\n")
        return "Voice not recognized"
    except sr.RequestError as e:
        output_box.insert(tk.END, f"⚠️ Request error: {e}\n")
        return f"Request error: {e}"
