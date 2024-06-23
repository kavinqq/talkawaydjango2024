from typing import TypedDict
from rest_framework import serializers


class ChatWithGPTTypedDict(TypedDict):
    chat_id: str
    scenario: str
    user_input: str
    user_input_base64: str


class ChatWithGPTSerializer(serializers.Serializer):
    chat_id = serializers.CharField(
        help_text="會話ID",
        allow_null=True,
        allow_blank=True,
        required=False
    )
    scenario = serializers.CharField(
        help_text="情景",
        allow_null=True,
        allow_blank=True,
        required=False
    )
    user_input = serializers.CharField(
        help_text="用戶輸入",
        allow_null=True,
        allow_blank=True,
        required=False
    )
    user_input_base64 = serializers.CharField(
        help_text="用戶輸入的base64語音",
        allow_null=True,
        allow_blank=True,
        required=False
    )

    @property
    def validated_data(self) -> ChatWithGPTTypedDict:
        return self._validated_data
