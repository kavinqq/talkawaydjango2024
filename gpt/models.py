from django.db import models

from open_ai_helper.gpt_chat import GPTChatRoleEnum


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    

    class Meta:
        verbose_name = '時間戳記'
        verbose_name_plural = '時間戳記'
        abstract = True


class ThirdPartyLogin(TimeStamped):
    login_platform = models.CharField(max_length=20, blank=True, null=True)
    login_id = models.CharField(max_length=100, unique=True)
    
    
class Chat(TimeStamped):
    chat_id = models.CharField(
        verbose_name="會話ID",
        max_length=50,
        unique=True
    )   
    
    history: models.Manager["ChatHistory"]
    
    class Meta:
        verbose_name = 'GPT會話'
        verbose_name_plural = 'GPT會話'
        
        indexes = [
            models.Index(fields=['chat_id']),
        ]
    
    
class ChatHistory(TimeStamped):
    role = models.CharField(
        max_length=50, 
        choices=GPTChatRoleEnum.choices,
        verbose_name='角色'
    )
    content = models.TextField(
        verbose_name='內容'
    )
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='GPT會話'
    )
    
    class Meta:
        verbose_name = '對話互動歷史紀錄'
        verbose_name_plural = '對話互動歷史紀錄'
        
        indexes = [
            models.Index(fields=['created_at']),
        ]