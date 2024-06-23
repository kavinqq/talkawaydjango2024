import logging

from django.conf import settings
from openai import OpenAI
from typing import IO


logger = logging.getLogger(__name__)


class STTHelper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(STTHelper, cls).__new__(cls)

        return cls._instance

    def __init__(self, *args, **kwargs):
        try:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        except Exception as e:
            logger.info(e, exc_info=True)
            raise Exception("OpenAI client error")
        
    def speech_to_text(
        self,
        file: IO[bytes]
    ) -> str:
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=file,
        )
        
        return transcription.text
    