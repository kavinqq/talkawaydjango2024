import io
import base64
import logging
from typing import List

from django.utils import timezone

import nanoid
from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiRequest,
    OpenApiResponse
)

from open_ai_helper.gpt_chat import ChatHelper
from open_ai_helper.gpt_tts import TTSHelper
from open_ai_helper.gpt_stt import STTHelper
from gpt.serializers import ChatWithGPTSerializer
from gpt.models import (
    Chat,
    ChatHistory
)
from constants.response_enum import (
    ResponseEnum,
    ResponseSerializer
)


logger = logging.getLogger(__name__)


class ChatWithGPTAPIView(GenericAPIView):
    serializer_class = ChatWithGPTSerializer
    default_condition = f"""
        I'm providing a scenario for a simulated conversation,
        and I would like to chat with you based on this scenario.
        However, I want you to randomly choose one of the roles in the scenario
        and initiate the conversation from that perspective.
        Please start the conversation with a single opening line from the chosen role's viewpoint in English.
        Final, don't need to specify who speak just chat like a person.
    """

    @extend_schema(
        request=OpenApiRequest(
            request=ChatWithGPTSerializer,
            examples=[
                OpenApiExample(
                    name="初次對話",
                    description="初次對話",
                    value={
                        "chat_id": None,
                        "scenario": "Imagine you are in a coffee shop in Seattle, and a person (male/female) starts talking to you.",
                        "user_input": None
                    }
                ),
                OpenApiExample(
                    name="接續對話",
                    description="接續對話",
                    value={
                        "chat_id": "20240615_1234",
                        "scenario": None,
                        "user_input_base64": "User voice base64 string..."
                    }
                )
            ]
        ),
        responses={
            200: OpenApiResponse(
                description="成功",
                response=ResponseSerializer,
                examples=[
                    OpenApiExample(
                        name="成功",
                        description="成功",
                        value=[
                            ResponseEnum.SUCCESS.response(
                                data={
                                    "chat_id": "20240615_1234",
                                    "content": "Hello, how are you?",
                                    "tts": "base64 encode string with utf-8(GPT回覆的語音)",
                                    "user_input": "Hello, how are you?"
                                }
                            )
                        ]
                    )
                ]
            )
        }
    )
    def post(self, request: Request):
        try:
            ser = self.serializer_class(data=request.data)
            ser.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            logger.info(e.detail, exc_info=True)
            return Response(e.detail, status=HTTP_400_BAD_REQUEST)

        validated_data = ser.validated_data
        chat_id = validated_data.get("chat_id")
        scenario = validated_data.get("scenario")
        user_input = validated_data.get("user_input")
        user_input_base64 = validated_data.get("user_input_base64")

        check_result, check_msg = self._check_input_param(
            chat_id=chat_id,
            scenario=scenario,
            user_input=user_input,
            user_input_base64=user_input_base64
        )
        if check_result is False:
            return Response(ResponseEnum.SUCCESS.response(data=check_msg), status=HTTP_400_BAD_REQUEST)
        
        user_input = user_input or self._convert_base64(user_input_base64)

        gpt_helper = ChatHelper()
        if chat_id:
            chat = Chat.objects.get(chat_id=chat_id)

            messages = [
                {
                    "role": data.role,
                    "content": data.content
                }
                for data in chat.history.order_by('created_at')
            ]

            gpt_response, history = gpt_helper.chat(
                user_input=user_input,
                history=messages
            )

            self._gen_history(chat, history[-2:])
        else:
            chat_id = f"{timezone.localtime().strftime('%Y%m%d')}_{nanoid.generate(size=4)}"
            
            gpt_response, history = gpt_helper.chat(system=f"{self.default_condition}\nScenario:{scenario}")
            
            chat = Chat.objects.create(
                chat_id=chat_id,
            )
            
            self._gen_history(chat, history)

        try:
            tts_helper = TTSHelper()
            tts_bytes = tts_helper.text_to_speech_bytes(gpt_response)
        except Exception as e:
            logger.info(e, exc_info=True)
            return Response(ResponseEnum.UNEXPECTED_ERROR.response(data=None), status=HTTP_400_BAD_REQUEST)

        payload = {
            "tts":tts_bytes,
            "chat_id": chat_id,
            "content": gpt_response,
            "user_input": user_input
        }

        return Response(ResponseEnum.SUCCESS.response(data=payload))

    def _check_input_param(
        self,
        chat_id: str,
        scenario: str,
        user_input: str,
        user_input_base64: str
    ) -> tuple[bool, str]:
        conditions = {
            (not chat_id and not scenario):
                "如果沒有提供 chat_id，則 scenario 必須提供。",
            (chat_id and not (user_input or user_input_base64)):
                "如果有提供 chat_id，則 user_input 或 user_input_base64 必須提供其一。"
        }
        for condition, message in conditions.items():
            if condition:
                return False, message

        return True, ""

    def _gen_history(self, chat: Chat, history: List[dict]) -> None:
        history_create_list = [
            ChatHistory(
                chat=chat,
                role=data.get("role"),
                content=data.get("content"),
            )
            for data in history
        ]
        ChatHistory.objects.bulk_create(history_create_list)

        return None

    def _convert_base64(self, base64_str: str) -> str:
        if not base64_str:
            return base64_str
        
        audio_bytes = base64.b64decode(base64_str)
        
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "user_input.mp3"
        
        stt_helper = STTHelper()
        user_input = stt_helper.speech_to_text(audio_file)
        
        return user_input    
 