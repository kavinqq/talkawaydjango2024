from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('gcp/', include('gcp.urls')),
    path('gpt/', include('gpt.urls')),
    path('api-auth/', include('rest_framework.urls'))
]
