from rest_framework import serializers


class ChatWithGPTSerializer(serializers.Serializer):
    session_id = serializers.CharField(help_text="會話ID", allow_null=False, allow_blank=False, required=False)
    scenario = serializers.CharField(help_text="情景", allow_null=False, allow_blank=False, required=False)
    input_text = serializers.CharField(help_text="給ChatGPT的內容", allow_null=False, allow_blank=False, required=False)
