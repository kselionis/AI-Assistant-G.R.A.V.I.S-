import speech_recognition as sr
import wikipedia
import edge_tts 
import asyncio 
import pygame
import os
import time
import datetime
import webbrowser
import cv2
import pyautogui
from PIL import Image
from google import genai
import threading
import customtkinter as ctk
import pywhatkit # Για YouTube
import psutil # Για μπαταρία/CPU
import winshell
import re
import unicodedata
import httpx

# --- ΡΥΘΜΙΣΕΙΣ ---

def load_api_key():
    env_key = os.getenv("GEMINI_API_KEY", "").strip()
    if env_key:
        return env_key

    key_file = os.path.join(os.path.dirname(__file__), "gemini_api_key")
    if os.path.exists(key_file):
        with open(key_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


API_KEY = load_api_key()
MODEL_NAME = "gemini-2.5-flash"
WAKE_WORDS = ["jarvis", "tzarvis", "τζαρβις", "assistant", "βοηθε", "voithe"]

# Ρυθμίσεις Εμφάνισης
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class JarvisGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("J.A.R.V.I.S. Systems")
        self.geometry("600x500")
        self.resizable(False, False)
        
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.label_title = ctk.CTkLabel(self.main_frame, text="● J.A.R.V.I.S.", font=("Roboto Medium", 24), text_color="#00E5FF")
        self.label_title.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.main_frame, text="SYSTEMS INITIALIZING...", font=("Roboto", 14), text_color="gray")
        self.status_label.pack(pady=5)

        self.chat_box = ctk.CTkTextbox(self.main_frame, width=500, height=300, font=("Consolas", 12))
        self.chat_box.pack(pady=10)
        self.chat_box.configure(state="disabled")

        self.btn_quit = ctk.CTkButton(self.main_frame, text="SHUTDOWN", fg_color="#CF0000", hover_color="#8F0000", command=self.close_app)
        self.btn_quit.pack(pady=10)
        
        self.running = True

    # --- SAFE GUI UPDATES (Το μυστικό για να μην κολλάει) ---
    def safe_update_status(self, text, color):
        self.after(0, lambda: self.status_label.configure(text=text, text_color=color))

    def safe_log_message(self, sender, message):
        def _log():
            self.chat_box.configure(state="normal")
            self.chat_box.insert("end", f"[{sender}]: {message}\n\n")
            self.chat_box.see("end")
            self.chat_box.configure(state="disabled")
        self.after(0, _log)

    def close_app(self):
        self.running = False
        self.destroy()


def init_ai_client():
    if not API_KEY:
        return None
    try:
        return genai.Client(api_key=API_KEY, http_options={"api_version": "v1"})
    except Exception as e:
        print(f"DEBUG: AI init error -> {e}")
        return None

app = JarvisGUI()
client = init_ai_client()

# --- ΛΕΙΤΟΥΡΓΙΕΣ ---

# Ρύθμιση Φωνής Edge-TTS
VOICE_BY_LANG = {
    "el": "el-GR-NestorasNeural",  # Ανδρική φυσική φωνή (πιο κοντά στον Jarvis)
    "en": "en-US-GuyNeural",
}
SPEED = "+20%" # Πόσο πιο γρήγορα θέλεις να μιλάει (παίξε με το +10% ή +30%)

def get_tts_voice(lang):
    return VOICE_BY_LANG.get(lang, VOICE_BY_LANG["el"])


async def _generate_audio(text, voice):
    """Βοηθητική συνάρτηση για τη δημιουργία ήχου"""
    communicate = edge_tts.Communicate(text, voice, rate=SPEED)
    await communicate.save("voice.mp3")

def speak(text, lang=None):
    if not text: return

    resolved_lang = lang or detect_language(text)
    voice = get_tts_voice(resolved_lang)
    
    # GUI Updates
    app.safe_update_status("SPEAKING...", "#00FF00")
    app.safe_log_message("JARVIS", text)
    print(f"DEBUG: Jarvis saying ({resolved_lang}, {voice}) -> {text}")
    
    try:
        # Καλούμε την ασύγχρονη συνάρτηση του Edge-TTS
        asyncio.run(_generate_audio(text, voice))
        
        # Αναπαραγωγή
        pygame.mixer.init()
        pygame.mixer.music.load("voice.mp3")
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            if not app.running: 
                pygame.mixer.music.stop()
                break
            pygame.time.Clock().tick(10)
            
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.quit()
        
        # Καθαρισμός
        time.sleep(0.1)
        if os.path.exists("voice.mp3"):
            os.remove("voice.mp3")
            
    except Exception as e:
        print(f"DEBUG Error Audio: {e}")
    
    app.safe_update_status("IDLE", "gray")


def ask_ai(prompt, image_context=None, system_instruction=None):
    if client is None:
        return "Δεν έχω ενεργό κλειδί AI. Βάλε GEMINI_API_KEY και κάνε επανεκκίνηση."

    full_prompt = prompt
    if system_instruction:
        full_prompt = f"{system_instruction}\nΧρήστης: {prompt}"

    contents = [full_prompt]
    if image_context is not None:
        contents.append(image_context)

    for attempt in range(2):
        try:
            response = client.models.generate_content(model=MODEL_NAME, contents=contents)
            text = getattr(response, "text", "")
            return text.strip() if text else "Δεν έχω απάντηση αυτή τη στιγμή."
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            print(f"DEBUG: AI network error (attempt {attempt + 1}) -> {e}")
            if attempt == 0:
                time.sleep(1)
                continue
            return "Έχω προσωρινό πρόβλημα σύνδεσης με το AI. Δοκίμασε ξανά σε λίγο."
        except Exception as e:
            print(f"DEBUG: AI request error -> {e}")
            error_text = str(e).lower()
            if "api key" in error_text or "unauthorized" in error_text or "permission" in error_text:
                return "Το AI key φαίνεται μη έγκυρο ή χωρίς πρόσβαση. Έλεγξε το GEMINI_API_KEY."
            if "quota" in error_text or "429" in error_text or "rate" in error_text:
                return "Έφτασα προσωρινά το όριο αιτημάτων AI. Περίμενε λίγο και ξαναδοκίμασε."
            return "Το AI module έχει προσωρινό πρόβλημα. Προσπάθησε ξανά."


def normalize_text(text):
    if not text:
        return ""
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"\s+", " ", text)
    return text


def detect_language(text):
    if not text:
        return "el"
    greek_chars = sum(1 for ch in text if "\u0370" <= ch <= "\u03ff")
    normalized = normalize_text(text)
    english_hints = ["open", "play", "help", "time", "status", "shutdown", "sleep", "wake"]
    english_hits = sum(1 for hint in english_hints if hint in normalized)
    if greek_chars > 0:
        return "el"
    if english_hits > 0:
        return "en"
    return "en"


def localized(lang, el_text, en_text):
    return el_text if lang == "el" else en_text


def contains_any(text, terms):
    return any(term in text for term in terms)


def remove_terms(text, terms):
    out = text
    for term in terms:
        out = re.sub(re.escape(term), "", out, flags=re.IGNORECASE)
    return " ".join(out.split())


def has_wake_word(command):
    normalized = normalize_text(command)
    return any(w in normalized for w in WAKE_WORDS)


def remove_wake_word(command):
    cleaned = command
    wake_variants = ["jarvis", "tzarvis", "τζάρβις", "τζαρβις", "assistant", "βοηθέ", "βοηθε", "voithe"]
    for w in wake_variants:
        cleaned = re.sub(re.escape(w), "", cleaned, flags=re.IGNORECASE)
    return " ".join(cleaned.split())


def get_battery_percent():
    battery = psutil.sensors_battery()
    if battery is None:
        return "άγνωστο"
    return str(battery.percent)


def save_note(note):
    with open("notes.txt", "a", encoding="utf-8") as f:
        stamp = datetime.datetime.now().strftime("%d/%m %H:%M")
        f.write(f"[{stamp}] {note}\n")


def read_recent_notes(char_limit=350):
    if not os.path.exists("notes.txt"):
        return "Δεν υπάρχουν σημειώσεις ακόμα."
    with open("notes.txt", "r", encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        return "Το αρχείο σημειώσεων είναι άδειο."
    return text[-char_limit:]


def open_quick_target(target):
    apps = {
        "notepad": "notepad.exe",
        "σημειωματάριο": "notepad.exe",
        "calculator": "calc.exe",
        "υπολογιστής": "calc.exe",
        "paint": "mspaint.exe",
    }

    normalized = target.strip().lower()
    if normalized in apps:
        os.system(f"start {apps[normalized]}")
        return True

    if "." in normalized and " " not in normalized:
        webbrowser.open(f"https://{normalized}")
        return True

    if normalized:
        webbrowser.open(f"https://www.google.com/search?q={normalized}")
        return True

    return False


def parse_shutdown_minutes(command):
    nums = re.findall(r"\d+", command)
    if not nums:
        return None
    return int(nums[0])


def handle_command(command, lang, system_instruction):
    normalized = normalize_text(command)
    respond = lambda el_text, en_text: speak(localized(lang, el_text, en_text))

    if contains_any(normalized, ["βοηθεια", "τι μπορεις να κανεις", "help", "what can you do"]):
        respond(
            "Μπορώ να ψάξω web, να παίξω μουσική, να κρατήσω σημειώσεις, να σου πω ώρα, να ανοίξω εφαρμογές και να απαντήσω με AI.",
            "I can search the web, play music, save notes, tell the time, open apps, and answer with AI.",
        )
        return True

    if contains_any(normalized, ["βικιπαιδεια", "wikipedia"]):
        search_term = remove_terms(command, ["βικιπαίδεια", "βικιπαιδεια", "wikipedia"]).strip()
        if not search_term:
            respond("Τι να ψάξω στη Βικιπαίδεια;", "What should I search on Wikipedia?")
            return True
        respond(f"Ψάχνω για {search_term}.", f"Searching for {search_term}.")
        try:
            summary = wikipedia.summary(search_term, sentences=2)
            speak(summary)
        except Exception:
            respond("Δεν βρήκα αποτέλεσμα.", "I could not find a result.")
        return True

    if contains_any(normalized, ["ανοιξε", "open"]):
        target = remove_terms(command, ["άνοιξε το", "ανοιξε το", "άνοιξε", "ανοιξε", "open"]).strip()
        if open_quick_target(target):
            respond(f"Έγινε. Άνοιξα {target}.", f"Done. Opened {target}.")
        else:
            respond("Δεν κατάφερα να το ανοίξω.", "I could not open that.")
        return True

    if contains_any(normalized, ["αναφορα", "καλημερα", "daily briefing", "briefing"]):
        now = datetime.datetime.now()
        if lang == "el":
            prompt = (
                f"Ώρα {now.strftime('%H:%M')}, ημερομηνία {now.strftime('%d/%m/%Y')}, "
                f"μπαταρία {get_battery_percent()}%. Δώσε σύντομη ημερήσια αναφορά 2 προτάσεων στα Ελληνικά."
            )
        else:
            prompt = (
                f"Time {now.strftime('%H:%M')}, date {now.strftime('%d/%m/%Y')}, "
                f"battery {get_battery_percent()}%. Give a short daily briefing in 2 sentences in English."
            )
        speak(ask_ai(prompt, system_instruction=system_instruction))
        return True

    if contains_any(normalized, ["κατασταση", "system status", "status"]):
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory().percent
        battery = get_battery_percent()
        respond(
            f"CPU {cpu} τοις εκατό, μνήμη {mem} τοις εκατό, μπαταρία {battery} τοις εκατό.",
            f"CPU {cpu} percent, memory {mem} percent, battery {battery} percent.",
        )
        return True

    if "καθαρισε" in normalized and contains_any(normalized, ["σκουπιδια", "recycle", "bin"]):
        try:
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            respond("Ο κάδος ανακύκλωσης καθαρίστηκε.", "The recycle bin has been emptied.")
        except Exception:
            respond("Δεν κατάφερα να καθαρίσω τον κάδο.", "I could not empty the recycle bin.")
        return True

    if contains_any(normalized, ["τερματισμος σε", "shutdown in"]):
        mins = parse_shutdown_minutes(command)
        if mins is None:
            respond("Πες μου τα λεπτά για τερματισμό.", "Tell me how many minutes before shutdown.")
            return True
        os.system(f"shutdown /s /t {mins * 60}")
        respond(f"Τερματισμός σε {mins} λεπτά.", f"Shutdown scheduled in {mins} minutes.")
        return True

    if "ακυρωσε" in normalized and contains_any(normalized, ["τερματισμο", "shutdown"]):
        os.system("shutdown /a")
        respond("Ακύρωσα τον τερματισμό.", "I canceled the shutdown.")
        return True

    if contains_any(normalized, ["σημειωσε", "note this", "take note"]):
        note = remove_terms(command, ["σημείωσε", "σημειωσε", "note this", "take note"]).strip()
        if not note:
            respond("Πες μου τι να σημειώσω.", "Tell me what to note.")
            return True
        save_note(note)
        respond("Η σημείωση αποθηκεύτηκε.", "The note has been saved.")
        return True

    if contains_any(normalized, ["διαβασε σημειωσεις", "διαβασε τις σημειωσεις", "read notes", "show notes"]):
        prefix = localized(lang, "Οι τελευταίες σημειώσεις είναι: ", "Your latest notes are: ")
        speak(prefix + read_recent_notes())
        return True

    if normalized.startswith("παιξε") or normalized.startswith("play"):
        song = remove_terms(command, ["παίξε", "παιξε", "play"]).strip()
        if not song:
            respond("Ποιο τραγούδι θέλεις;", "Which song do you want?")
            return True
        respond(f"Παίζω {song} στο YouTube.", f"Playing {song} on YouTube.")
        pywhatkit.playonyt(song)
        return True

    if contains_any(normalized, ["ωρα", "τι ωρα", "time"]):
        if lang == "el":
            speak(datetime.datetime.now().strftime("Η ώρα είναι %H:%M"))
        else:
            speak(datetime.datetime.now().strftime("The time is %H:%M"))
        return True

    if contains_any(normalized, ["δυναμωσε", "volume up", "sound up"]):
        pyautogui.press("volumeup", presses=5)
        respond("Αύξησα την ένταση.", "I increased the volume.")
        return True

    if contains_any(normalized, ["χαμηλωσε", "volume down", "sound down"]):
        pyautogui.press("volumedown", presses=5)
        respond("Μείωσα την ένταση.", "I lowered the volume.")
        return True

    if contains_any(normalized, ["screenshot", "στιγμιοτυπο", "φωτογραφια οθονης"]):
        filename = f"screen_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pyautogui.screenshot(filename)
        respond(
            f"Έτοιμο. Αποθήκευσα το στιγμιότυπο ως {filename}.",
            f"Done. I saved the screenshot as {filename}.",
        )
        return True

    if contains_any(normalized, ["βλεπεις", "κοιτα", "τι βλεπεις", "look around", "what do you see"]):
        respond("Κοιτάζω τώρα.", "Looking now.")
        img = take_picture()
        if img is None:
            respond("Δεν έχω εικόνα από την κάμερα.", "I could not get an image from the camera.")
            return True
        vision_prompt = localized(lang, "Περιέγραψε σύντομα τι βλέπεις στην εικόνα.", "Briefly describe what you see in the image.")
        answer = ask_ai(vision_prompt, image_context=img, system_instruction=system_instruction)
        speak(answer)
        return True

    return False

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        app.safe_update_status("LISTENING...", "#FFD700")
        print("DEBUG: Listening...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            # Timeout για να μην παγώνει για πάντα
            audio = r.listen(source, timeout=3, phrase_time_limit=5)
            app.safe_update_status("PROCESSING...", "#00E5FF")
            print("DEBUG: Processing audio...")
            for lang in ("el-GR", "en-US"):
                try:
                    query = r.recognize_google(audio, language=lang)
                    print(f"DEBUG: Recognized ({lang}) -> {query}")
                    return query.lower()
                except sr.UnknownValueError:
                    continue
            raise sr.UnknownValueError()
        except sr.WaitTimeoutError:
            print("DEBUG: Timeout (Silence)")
            app.safe_update_status("IDLE", "gray")
            return ""
        except sr.UnknownValueError:
            print("DEBUG: Could not understand audio")
            app.safe_update_status("IDLE", "gray")
            return ""
        except Exception as e:
            print(f"DEBUG: Listen Error -> {e}")
            app.safe_update_status("IDLE", "gray")
            return ""

def take_picture():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            speak("Κάμερα μη διαθέσιμη.")
            return None
        time.sleep(0.5)
        ret, frame = cap.read()
        cap.release()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return Image.fromarray(rgb_frame)
    except Exception as e:
        print(f"Camera Error: {e}")
    return None

def run_jarvis_logic():
    print("DEBUG: Thread Started")
    time.sleep(2)
    
    # Cinematic Intro
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12: greeting = "Καλημέρα."
    elif 12 <= hour < 18: greeting = "Καλησπέρα."
    else: greeting = "Συστήματα ενεργά."
    speak(greeting)
    
    SYSTEM_INSTRUCTION_EL = "Είσαι ο J.A.R.V.I.S. Απάντα στα Ελληνικά, σύντομα, με αυτοπεποίθηση και χρήσιμες λεπτομέρειες."
    SYSTEM_INSTRUCTION_EN = "You are J.A.R.V.I.S. Respond in clear English, concise, confident, and helpful."
    
    active_listening = True 

    while app.running:
        time.sleep(0.1)
        command = listen()
        if not command:
            continue

        normalized_command = normalize_text(command)
        command_lang = detect_language(command)

        app.safe_log_message("USER", command)

        # --- ΛΕΙΤΟΥΡΓΙΑ ΥΠΝΟΥ / ΞΥΠΝΗΜΑΤΟΣ ---
        if contains_any(normalized_command, ["σταματα να ακους", "κοιμησου", "pause", "sleep mode"]):
            active_listening = False
            speak(localized(command_lang, "Μπαίνω σε αναμονή. Πες 'Ξύπνα' για να επιστρέψω.", "Entering standby. Say 'wake up' when you need me."))
            continue
        
        if contains_any(normalized_command, ["ξυπνα", "ενεργοποιηση", "wake up", "resume"]):
            active_listening = True
            speak(localized(command_lang, "Επέστρεψα. Σε ακούω.", "I'm back. I'm listening."))
            continue

        if not active_listening:
            continue

        if contains_any(normalized_command, ["αντιο", "shutdown", "goodbye", "bye"]):
            speak(localized(command_lang, "Κλείνω.", "Shutting down."))
            app.after(2000, app.close_app)
            break

        # Για γενική χρήση ζητάμε wake-word όταν η εντολή είναι μικρή/ασαφής.
        if len(normalized_command.split()) <= 3 and not has_wake_word(command):
            continue

        normalized = remove_wake_word(command)
        if not normalized:
            speak(localized(command_lang, "Σε ακούω.", "I'm listening."))
            continue

        current_lang = detect_language(normalized)
        current_instruction = SYSTEM_INSTRUCTION_EL if current_lang == "el" else SYSTEM_INSTRUCTION_EN

        if handle_command(normalized, current_lang, current_instruction):
            continue

        # Fallback σε AI για κάθε άλλη φυσική γλώσσα.
        speak(ask_ai(normalized, system_instruction=current_instruction))

if __name__ == "__main__":
    # Ξεκινάμε το Thread
    thread = threading.Thread(target=run_jarvis_logic)
    thread.daemon = True
    thread.start()

    # Ξεκινάμε το GUI
    app.mainloop()