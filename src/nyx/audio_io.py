import speech_recognition as sr
import pyttsx3
import time as t

recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

def listen() -> str:
    """
    Listens to the user through microphone.
    Falls back to keyboard input if speech fails or times out.
    """
    try:
        with sr.Microphone() as source:
            print("🎤 Listening... (speak clearly)")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=10)
            text = recognizer.recognize_google(audio, language="en-US")
            print(f"🗣️ You said: {text}")
            return text
    except sr.WaitTimeoutError:
        print("⏳ Listening timed out. Try again.")
        return input("⌨️ Type instead: ")
    except sr.UnknownValueError:
        print("❌ Could not understand audio.")
        return input("⌨️ Type instead: ")
    except sr.RequestError as e:
        print(f"⚠️ Speech recognition service error: {e}")
        return input("⌨️ Type instead: ")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
        return input("⌨️ Type instead: ")

def speak(text: str):
    """
    Prints and speaks the assistant response reliably.
    """
    try:
        print(f"🤖 Nyx: {text}")  # Only one print
        tts_engine.stop()          # ✅ Clear any previous queued speech
        tts_engine.say(text)
        tts_engine.runAndWait()
        t.sleep(0.2)  # slight pause after speaking
    except Exception:
        print("(TTS failed)")
