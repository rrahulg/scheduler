import base64
import os

from text_to_speech import save


def play_audio(text):
    path = os.path.join(os.getcwd(), "data/output.mp3")
    save(text, lang="en", file=path)

    with open(path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")

    md = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    return md
