import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MURF_API_KEY = os.getenv("MURF_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")  # Default to 'tour-gpt35' if not set
AZURE_OPEN_AI_MODEL_ENDPOINT = os.getenv("AZURE_OPEN_AI_MODEL_ENDPOINT", "")  # Default endpoint
AZURE_OPEN_AI_MODEL_API_KEY = os.getenv("AZURE_OPEN_AI_MODEL_API_KEY", "3mZxBeyiQ446wX38qbiv1CkHqJ18gBhXFQjoBzavJ9tXRL3FoqRDJQQJ99BFACHYHv6XJ3w3AAAAACOGI0eR")  # Default API key
ORS_API_KEY = os.getenv("ORS_API_KEY")
AZURE_TRANSCRIBE_ENDPOINT = os.getenv("AZURE_TRANSCRIBE_ENDPOINT", "https://ironk-mcg85dcf-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-4o-transcribe/audio/transcriptions?api-version=2025-03-01-preview")   