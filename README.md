# G.R.A.V.I.S. Voice Assistant (English + Ελληνικά)

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A bilingual desktop AI assistant inspired by G.R.A.V.I.S., built with Python.
It supports voice commands, system actions, notes, screenshots, camera vision, and Gemini AI responses in both English and Greek.

## Demo

![G.R.A.V.I.S Demo](assets/demo.gif)

_Tip: Replace `assets/demo.gif` with your real screen recording GIF._

## Screenshots

![Main UI](assets/screenshots/main_ui.png)
![Voice Command](assets/screenshots/voice_command.png)

_Tip: Add your real images in `assets/screenshots/` and keep clear filenames._

---

## English

### Features
- Wake-word assistant mode (Gravis / Greek variants).
- Bilingual voice recognition: Greek (`el-GR`) and English (`en-US`).
- Bilingual speech output with automatic voice switching.
- Gemini AI integration (`gemini-2.5-flash`) for natural responses.
- GUI interface using CustomTkinter.
- Built-in commands:
  - help
  - Wikipedia search
  - open app/site/search target
  - daily briefing
  - system status (CPU/RAM/battery)
  - empty recycle bin
  - schedule/cancel shutdown
  - save/read notes
  - play song on YouTube
  - time
  - volume up/down
  - screenshot
  - camera scene description (vision)
- Sleep / wake listening mode.

### Project Structure
- `jarvis.py`: Main assistant app (GUI + voice + commands + AI fallback).
- `check.py`: Gemini connection/model check utility.
- `gemini_api_key`: Local API key file (fallback when env var is not set).

### Requirements
- Windows (recommended for current system actions).
- Python 3.10+
- Microphone and speakers
- Internet connection
- Gemini API key

### Installation
1. Install dependencies:

```bash
pip install SpeechRecognition wikipedia edge-tts pygame opencv-python pyautogui Pillow google-genai customtkinter pywhatkit psutil winshell pyaudio
```

2. Add your API key:
- Option A: set environment variable `GEMINI_API_KEY`
- Option B: put your key inside `gemini_api_key` (single line)

3. Verify Gemini connection:

```bash
python check.py
```

4. Run G.R.A.V.I.S:

```bash
python jarvis.py
```

### Example Voice Commands (English)
- "Gravis, help"
- "Gravis, open youtube.com"
- "Gravis, play Linkin Park Numb"
- "Gravis, take note buy milk"
- "Gravis, what time is it"
- "Gravis, system status"
- "Gravis, look around"
- "Gravis, sleep mode"
- "Gravis, wake up"

### Troubleshooting
- If microphone is not detected, check Windows privacy settings.
- If AI responses fail, verify your API key and run `python check.py`.
- If audio playback fails, ensure no other app is locking the output device.
- If camera command fails, verify camera permissions and device availability.

### Security Note
- Never commit your real API key to public repositories.
- Add `gemini_api_key` to `.gitignore` before pushing to GitHub.

---

## Ελληνικά

### Χαρακτηριστικά
- Λειτουργία wake-word (Gravis και ελληνικές παραλλαγές).
- Δίγλωσση αναγνώριση φωνής: Ελληνικά (`el-GR`) και English (`en-US`).
- Δίγλωσση εκφώνηση με αυτόματη αλλαγή φωνής ανά γλώσσα.
- Ενσωμάτωση Gemini AI (`gemini-2.5-flash`) για φυσικές απαντήσεις.
- Γραφικό περιβάλλον με CustomTkinter.
- Ενσωματωμένες εντολές:
  - βοήθεια
  - αναζήτηση στη Wikipedia
  - άνοιγμα εφαρμογής/ιστοσελίδας/αναζήτησης
  - ημερήσια αναφορά
  - κατάσταση συστήματος (CPU/RAM/μπαταρία)
  - καθάρισμα κάδου ανακύκλωσης
  - προγραμματισμός/ακύρωση τερματισμού
  - αποθήκευση/ανάγνωση σημειώσεων
  - αναπαραγωγή τραγουδιού στο YouTube
  - ώρα
  - ένταση ήχου πάνω/κάτω
  - screenshot
  - περιγραφή εικόνας από κάμερα (vision)
- Λειτουργία ύπνου/αφύπνισης.

### Δομή Project
- `jarvis.py`: Κύρια εφαρμογή βοηθού (GUI + φωνή + εντολές + AI fallback).
- `check.py`: Έλεγχος σύνδεσης και μοντέλων Gemini.
- `gemini_api_key`: Τοπικό αρχείο API key (fallback αν δεν υπάρχει env var).

### Απαιτήσεις
- Windows (προτείνεται για τις τρέχουσες system ενέργειες).
- Python 3.10+
- Μικρόφωνο και ηχεία
- Σύνδεση στο internet
- Gemini API key

### Εγκατάσταση
1. Εγκατάσταση dependencies:

```bash
pip install SpeechRecognition wikipedia edge-tts pygame opencv-python pyautogui Pillow google-genai customtkinter pywhatkit psutil winshell pyaudio
```

2. Βάλε το API key:
- Επιλογή A: env var `GEMINI_API_KEY`
- Επιλογή B: βάλε το key μέσα στο `gemini_api_key` (μία γραμμή)

3. Έλεγχος σύνδεσης Gemini:

```bash
python check.py
```

4. Εκκίνηση G.R.A.V.I.S:

```bash
python jarvis.py
```

### Παραδείγματα Φωνητικών Εντολών (Ελληνικά)
- «Γκράβις βοήθεια»
- «Γκράβις άνοιξε youtube.com»
- «Γκράβις παίξε Imagine Dragons Believer»
- «Γκράβις σημείωσε να πάρω γάλα»
- «Γκράβις τι ώρα είναι»
- «Γκράβις κατάσταση συστήματος»
- «Γκράβις τι βλέπεις»
- «Γκράβις κοιμήσου»
- «Γκράβις ξύπνα»

### Αντιμετώπιση Προβλημάτων
- Αν δεν πιάνει μικρόφωνο, έλεγξε τα Windows privacy permissions.
- Αν δεν απαντά το AI, έλεγξε το API key και τρέξε `python check.py`.
- Αν δεν παίζει ήχο, έλεγξε αν άλλη εφαρμογή κρατά τη συσκευή εξόδου.
- Αν αποτυγχάνει η κάμερα, έλεγξε άδειες και διαθεσιμότητα συσκευής.

### Σημείωση Ασφαλείας
- Μην ανεβάζεις πραγματικό API key σε public repository.
- Πρόσθεσε το `gemini_api_key` στο `.gitignore` πριν κάνεις push στο GitHub.
