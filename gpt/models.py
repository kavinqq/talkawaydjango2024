from django.db import models


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    

    class Meta:
        abstract = True


class ThirdPartyLogin(TimeStamped):
    login_platform = models.CharField(max_length=20, blank=True, null=True)
    login_id = models.CharField(max_length=100, unique=True)
    
    
class Session(TimeStamped):
    session_id = models.CharField(max_length=50, unique=True)
    scenario = models.TextField(verbose_name='開始情景')
    
    
class SessionInteractions(TimeStamped):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='interactions')
    gpt_response = models.TextField(verbose_name='GPT回應', blank=True, null=True)
    user_input = models.TextField(verbose_name='使用者輸入', blank=True, null=True)
    