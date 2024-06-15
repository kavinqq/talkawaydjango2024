import base64
import logging
from enum import Enum

from django.conf import settings
from openai import OpenAI


logger = logging.getLogger(__name__)


class TTSVoiceEnum(Enum):
    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"


class TTSHelper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TTSHelper, cls).__new__(cls)

        return cls._instance

    def __init__(self, *args, **kwargs):
        try:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        except Exception as e:
            logger.info(e, exc_info=True)
            raise Exception("OpenAI client error")

    def text_to_speech_bytes(self, input: str, voice: str = TTSVoiceEnum.ALLOY.value) -> None:
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=input
        )

        audio_bytes = response.read()
        base64_encoded_data = base64.b64encode(audio_bytes).decode('utf-8')

        audio_bytes = base64.b64decode(base64_encoded_data)

        return audio_bytes
    