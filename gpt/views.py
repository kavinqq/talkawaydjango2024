import logging
import datetime

from django.conf import settings

import nanoid
from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from openai import OpenAI


from gpt.serializers import ChatWithGPTSerializer
from gpt.models import (
    Session,
    SessionInteractions
)


logger = logging.getLogger(__name__)


class ChatWithGPTAPIView(GenericAPIView):
    serializer_class = ChatWithGPTSerializer
    chat_gpt_model = "gpt-3.5-turbo"

    def post(self, request):
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        try:
            ser = self.serializer_class(data=request.data)                        
            ser.is_valid(raise_exception=True)

            session_id = ser.validated_data.get("session_id")
            scenario = ser.validated_data.get("scenario")
            input_text = ser.validated_data.get("input_text")
        except serializers.ValidationError as e:
            return Response(e.detail, status=HTTP_400_BAD_REQUEST)

        # 持續談話
        if session_id:
            session = Session.objects.get(session_id=session_id)

            interactions = session.interactions.all().order_by('created_at')

            messages = []
            for interaction in interactions:
                if interaction.gpt_response:
                    messages.append(
                        {
                            "role": "system",
                            "content": interaction.gpt_response
                        }
                    )
                if interaction.user_input:
                    messages.append(
                        {
                            "role": "user",
                            "content": interaction.user_input
                        }
                    )

            messages.append(
                {
                    "role": "system",
                    "content": input_text
                }
            )
        else:
            # 替代情景中的詞彙
            scenario = scenario.replace("想像你", "想像我").replace("想像", "想像我")
            
            # 詢問條件
            request_condition = "1.扮演這位(第三人) 2.前面不要加扮演的角色名字 3.講一句話開始談話 4.請用英文"

            messages = [
                {
                    "role": "system",
                    "content": f"{scenario}。{request_condition}"
                }
            ]
            
            session_id = f"{datetime.datetime.now().strftime('%Y%m%d')}-{nanoid.generate(size=6)}"                        
            
            session = Session.objects.create(
                        session_id=session_id,
                        scenario=scenario                
                    )                    
        
        # 根據gpt-3.5-turbo模型回應建立一個新的互動
        new_interaction = SessionInteractions.objects.create(
                            session=session,
                            gpt_response="",
                            user_input=input_text
                        )

        response = client.chat.completions.create(
            model=self.chat_gpt_model,
            messages=messages
        )

        # 解析回傳的結果
        result_list = []
        for choice in response.choices:
            result_list.append(choice.message.content)

        # combine gpt response
        result = "".join(result_list)

        # store gpt response
        new_interaction.gpt_response = result
        new_interaction.save()

        # return data
        payload = {
            "code": "000",
            "message": "success",
            "data": {
                "session_id": session_id,
                "gpt_response": result
            }
        }

        return Response(payload)
