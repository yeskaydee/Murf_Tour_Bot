from openai import AzureOpenAI
# from azure.core.credentials import AzureKeyCredential
from cfg import AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT, AZURE_OPEN_AI_MODEL_ENDPOINT, AZURE_OPEN_AI_MODEL_API_KEY

DEPLOYMENT_NAME = AZURE_OPENAI_DEPLOYMENT

def generate_tour_guide_reply(user_text, lat, lon, location_hint=None):
    system_prompt = (
        "You are a friendly and knowledgeable virtual tour guide. "
        "Answer tourist questions clearly and concisely. "
    )
    system_prompt += f"Assume the user coordinates are: {lat if lat else ''}, {lon if lon else ''}. This is the user's current location. {location_hint if location_hint else ''} "

    try:
        client = AzureOpenAI(
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPEN_AI_MODEL_ENDPOINT,
            api_key=AZURE_OPEN_AI_MODEL_API_KEY
        )

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_text,
                }
            ],
            max_tokens=4096,
            temperature=1.0,
            top_p=1.0,
            model=AZURE_OPENAI_DEPLOYMENT
        )

        reply = response.choices[0].message.content
        print(f"[LLM] User: {user_text}\n[LLM] Reply: {reply}")
        return reply
    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return "I'm sorry, I couldn't find an answer right now."
    
def extract_destination_from_query(user_query):
    """
    Uses the Azure OpenAI LLM to extract destination place from a user query like:
    "How do I get to Red Fort?"
    """
    try:
        client = AzureOpenAI(
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPEN_AI_MODEL_ENDPOINT,
            api_key=AZURE_OPEN_AI_MODEL_API_KEY
        )

        print(f"[LLM EXTRACT] User query: {user_query}")

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a location-aware assistant that extracts a destination address or place name only when the user is explicitly asking for directions "
                        "(e.g., 'how to go to...', 'give me directions to...', 'how far is...').\n\n"

                        "Follow these rules:\n\n"
 
                        "1. If the user asks for directions to a destination — either an address (e.g., '4th Street, A Nagar, Chennai') or a landmark (e.g., 'Red Fort') — first check whether the destination name is valid and correctly formatted.\n\n"

                        "2. If the destination is misspelled, ambiguous, or not properly structured, intelligently infer and autocorrect the intended place name — as you have access to Maps. Use spelling similarity, phonetics, context, and known nearby landmarks to determine the most likely intended location. Then return the cleaned and corrected destination name in a standard format, suitable for geocoding or routing.\n\n"

                        "3. If the user query does not contain an intent to get directions (e.g., questions like 'who built the Taj Mahal?' or 'are there cabs from Agra station to the Taj Mahal?'), you must return:\nNONE\n\n"

                        "4. If the user asks for directions but the destination is missing or not identifiable, also return:\nNONE\n\n"

                        "Output only the cleaned-up destination name or 'NONE'. Do not include any explanation or extra text."
                    )
                },
                {
                    "role": "user",
                    "content": user_query,
                }
            ],
            max_tokens=20,
            temperature=0.2,
            top_p=1.0,
            model=AZURE_OPENAI_DEPLOYMENT
        )
        print(f"[LLM EXTRACT] Response: {response.choices[0]}")

        destination = response.choices[0].message.content.strip()
        return None if destination.lower() == "none" else destination

    except Exception as e:
        print(f"[LLM EXTRACT ERROR] {e}")
        return None