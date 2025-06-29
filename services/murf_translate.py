from cfg import MURF_API_KEY
from murf import Murf

client = Murf(api_key=MURF_API_KEY)

def translate_text(text: str, target_lang) -> str:
    try:
        print(f"[TRANSLATE] Translating text: {text} to {target_lang}")
        response = client.text.translate(
            target_language=target_lang,
            texts=[text]
        )
        translated = response.translations[0].translated_text
        print(f"[TRANSLATE] {text} → {translated}")
        return translated or text
    except Exception as e:
        print(f"[TRANSLATE ERROR] {e}")
        return text  # Fallback to original if failed
