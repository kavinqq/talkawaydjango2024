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
                        "input_text": None
                    }
                ),
                                OpenApiExample(
                    name="接續對話",
                    description="接續對話",
                    value={
                        "chat_id": "20240615_1234",
                        "scenario": None,
                        "input_text": "Hi, how are you?"
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
                                    "tts": "base64 encode string with utf-8"
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
        input_text = validated_data.get("input_text")
        
        if not chat_id and not scenario and not input_text:
            return Response(ResponseEnum.UNEXPECTED_ERROR.response(data="至少需要一個參數"))
        
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
                user_input=input_text,
                history=messages
            )
            
            self._gen_history(chat, history[-2:])
        else:
            gpt_response, history = gpt_helper.chat(system=f"{self.default_condition}\nScenario:{scenario}")
            
            chat = Chat.objects.create(
                chat_id=f"{timezone.localtime().strftime('%Y%m%d')}_{nanoid.generate(size=4)}",
            )            

            self._gen_history(chat, history)            

        try:
            tts_helper = TTSHelper()
            tts_bytes = tts_helper.text_to_speech_bytes(gpt_response)
        except Exception as e:
            logger.info(e, exc_info=True)
            return Response(ResponseEnum.UNEXPECTED_ERROR.response(data=None))

        payload = {
            "chat_id": chat_id,
            "content": gpt_response,
            "tts":tts_bytes
        }

        return Response(ResponseEnum.SUCCESS.response(data=payload))
    
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
