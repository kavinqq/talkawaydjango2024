import logging
import datetime

import nanoid
from django.conf import settings
from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from openai import OpenAI


from gpt.serializers import ChatWithGPTSerializer, DellETestSerializer
from gpt.models import (
    Session,
    SessionInteractions
)


logger = logging.getLogger(__name__)


class ChatWithGPTAPIView(GenericAPIView):
    serializer_class = ChatWithGPTSerializer
    chat_gpt_model = "gpt-4o"

    def post(self, request):
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        try:
            ser = self.serializer_class(data=request.data)                        
            ser.is_valid(raise_exception=True)

            session_id = ser.validated_data.get("session_id")
            scenario = ser.validated_data.get("scenario")
            input_text = ser.validated_data.get("input_text")
        except serializers.ValidationError as e:
            logger.info(e.detail)
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
            # scenario = scenario.replace("想像你", "想像我").replace("想像", "想像我")
            # logger.info(f"{scenario=}")
            
            # 詢問條件
            # request_condition = f"""
            #    I'm providing a scenario for a simulated conversation,
            #    and I would like to chat with you based on this scenario.
            #    However, I want you to randomly choose one of the roles in the scenario
            #    and initiate the conversation from that perspective.
            #    Please start the conversation with a single opening line from the chosen role's viewpoint, in English.  
            #    Final, don't need to specify who speak just chat like a person.
            # """

            messages = [
                {
                    "role": "system",
                    "content": input_text
                }
            ]
            
            session_id = f"{datetime.datetime.now().strftime('%Y%m%d')}-{nanoid.generate(size=6)}"                        
            
            # session = Session.objects.create(
            #             session_id=session_id,
            #             scenario=scenario                
            #         )                    
        
        # 根據gpt-3.5-turbo模型回應建立一個新的互動
        # new_interaction = SessionInteractions.objects.create(
        #                     session=session,
        #                     gpt_response="",
        #                     user_input=input_text
        #                 )

        response = client.chat.completions.create(
            model=self.chat_gpt_model,
            messages=messages,
            max_tokens=100
        )
        
        logger.info(f"{response.__dict__=}")

        # 解析回傳的結果
        result_list = []
        for choice in response.choices:
            result_list.append(choice.message.content)

        # combine gpt response
        result = "".join(result_list)

        # store gpt response
        # new_interaction.gpt_response = result
        # new_interaction.save()

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


class DellETestAPIView(GenericAPIView):
    serializer_class = DellETestSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        valid_data = serializer.validated_data
        input_text = valid_data.get("input_text")
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=input_text,
            size="480x480",
            quality="standard",
            n=1
        )
        
        image_url = response.data[0].url
        
        return Response({
            "code": "000",
            "message": "success",
            "data": {
                "image_url": image_url
            }
        })