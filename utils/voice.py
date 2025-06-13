import wave

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def wave_file(pcm, filename="data/output.wav", channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)


client = genai.Client()


def save(text, client=client):
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Kore",
                    )
                )
            ),
        ),
    )
    candidate = response.candidates[0]
    if not candidate.content or not candidate.content.parts:
        raise ValueError(
            "Model did not return audio. Check API key access and model support."
        )

    data = candidate.content.parts[0].inline_data.data
    wave_file(data)
