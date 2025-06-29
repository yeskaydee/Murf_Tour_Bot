import asyncio
import os
import tempfile
import websockets
import uuid
import json
import base64
from bot.utils import save_wav
from Variables import VOICE_MAP

SAMPLE_RATE = 44100
WS_URL = "wss://api.murf.ai/v1/speech/stream-input"

async def murf_websocket_tts(text, target_lang):
    voice_id = VOICE_MAP.get(target_lang, "en-US-natalie")
    output_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.wav")
    print(f"[TTS] Connecting to Murf WebSocket at {WS_URL}")

    try:
        async with websockets.connect(
            f"{WS_URL}?api-key={os.getenv('MURF_API_KEY')}&sample_rate={SAMPLE_RATE}&channel_type=MONO&format=WAV"
        ) as ws:
            print("[TTS] WebSocket connection established.")

            await ws.send(json.dumps({
                "voice_config": {
                    "voiceId": voice_id,
                    "style": "Conversational",
                    "rate": 0,
                    "pitch": 0,
                    "variation": 1
                }
            }))
            print("[TTS] Sent voice config to Murf.")

            await asyncio.sleep(0.2)
            await ws.send(json.dumps({"text": text, "end": True}))
            print(f"[TTS] Sent text for synthesis: {text}")

            audio_data = bytearray()
            first_chunk = True
            while True:
                response = await ws.recv()
                data = json.loads(response)
                if "error" in data:
                    print(f"[TTS] Murf API Error: {data['error']}")
                    break
                if "audio" in data:
                    print("[TTS] Received audio chunk.")
                    audio_bytes = base64.b64decode(data["audio"])
                    print(f"[TTS] Received audio bytes: {len(audio_bytes)} bytes")

                    if first_chunk and len(audio_bytes) > 44:
                        audio_bytes = audio_bytes[44:]
                        first_chunk = False
                    audio_data.extend(audio_bytes)
                if str(data.get("final")).lower() == "true":
                    print("[TTS] Final audio chunk received.")
                    break
            save_wav(bytes(audio_data), output_path)
            print(f"[TTS] Saved synthesized audio to: {output_path}")
        return output_path
    except Exception as e:
        print(f"[WebSocket Error]: {e}")
        return None
