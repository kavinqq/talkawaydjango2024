import logging
from typing import Union, Tuple, List
from enum import Enum

from openai import OpenAI
from openai.types.chat import ChatCompletion
from django.conf import settings
from django.db.models import TextChoices


logger = logging.getLogger(__name__)


class GPTModelEnum(Enum):
    GPT_4O = "gpt-4o"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"


class GPTChatRoleEnum(TextChoices):
    SYSTEM = "system", "系統設定"
    USER = "user", "使用者輸入"
    ASSISTANT = "assistant", "系統回應"


class ChatHelper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChatHelper, cls).__new__(cls)

        return cls._instance

    def __init__(self, *args, **kwargs):
        try:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        except Exception as e:
            logger.info(e, exc_info=True)
            raise Exception("OpenAI client error")

    def chat(
        self,
        user_input: Union[str, None] = None,
        system: Union[None, str] = None,
        history: Union[None, list] = None,
        model: str =GPTModelEnum.GPT_3_5_TURBO.value
    )-> Tuple[str, List[dict]]:
        """和GPT模型進行對話

        Args:
            user_input (Union[str, None], optional): 使用者輸入. Defaults to None.
            system (Union[None, str], optional): 系統設定. Defaults to None.
            history (Union[None, list], optional): 歷史對話紀錄. Defaults to None.
            model (str, optional): GPT模型選擇 Defaults to GPTModelEnum.GPT_3_5_TURBO.value.

        Raises:
            Exception: user_input or system or history 至少需要一個

        Returns:
            Tuple[str, list]: GPT回應, 歷史對話紀錄
        """

        if history:
            messages = history
            messages.append(
            {
                "role": GPTChatRoleEnum.USER.value,
                "content": user_input
            }
        )
        elif system:
            messages = [
                {
                    "role": GPTChatRoleEnum.SYSTEM.value,
                    "content": system
                }
            ]
        elif user_input:
            messages = [
                {
                    "role": GPTChatRoleEnum.USER.value,
                    "content": user_input
                }
            ]
        else:
            raise Exception("user_input or system or history is required")
        
        gpt_response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=100
        )
        convert_response = self.convert_gpt_response(gpt_response)
        
        messages.append(
            {
                "role": GPTChatRoleEnum.ASSISTANT.value,
                "content": convert_response
            }
        )
        
        return convert_response, messages
        
        
    def convert_gpt_response(self, gpt_response: ChatCompletion):
        result_list = [
            choice.message.content
            for choice in gpt_response.choices
        ]
        
        return "".join(result_list)