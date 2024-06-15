from enum import Enum
from typing import (    
    Union,
    TypedDict
)

from rest_framework import serializers


class ResponseTypedDict(TypedDict):
    code: str
    cust_msg: str
    data: Union[None, dict, list]


class ResponseEnum(Enum):
    SUCCESS = ("0", "成功")
    UNEXPECTED_ERROR = ("999", "無法預期的錯誤")
    
    def __init__(
        self,
        code: str,
        msg: str
    ):
        self.code = code
        self.msg = msg
    
    def response(
        self,
        cust_msg: Union[str, None] = None,
        data: Union[None, dict, list] = None,
    ) -> ResponseTypedDict:
        return {
            "code": self.code,
            "msg": cust_msg if cust_msg else self.msg,
            "data": data
        }
        

class ResponseSerializer(serializers.Serializer):
    code = serializers.CharField(
        help_text="回傳代碼",
    )
    msg = serializers.CharField(
        help_text="回傳訊息",
    )
    data = serializers.JSONField(
        help_text="回傳資料",
        allow_null=True,  
    )
