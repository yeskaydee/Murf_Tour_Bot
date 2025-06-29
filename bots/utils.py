import wave

def save_wav(audio_data: bytes, output_path: str, sample_rate: int = 44100):
    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data)
