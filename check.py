from google import genai
import os


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

if not API_KEY:
    raise SystemExit("Δεν βρέθηκε κλειδί. Βάλε GEMINI_API_KEY ή αρχείο gemini_api_key.")

client = genai.Client(api_key=API_KEY, http_options={"api_version": "v1"})

print("--- Ψάχνω για διαθέσιμα μοντέλα... ---")
try:
    found = False
    for m in client.models.list():
        model_name = getattr(m, "name", "")
        if model_name:
            print(f"Βρέθηκε: {model_name}")
            found = True

    if not found:
        print("Δεν επιστράφηκαν μοντέλα από το API.")
except Exception as e:
    print(f"Σφάλμα: {e}")