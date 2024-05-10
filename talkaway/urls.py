from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('gcp/', include('gcp.urls')),
    path('gpt/', include('gpt.urls')),
    path('api-auth/', include('rest_framework.urls'))
]
urlpatterns += staticfiles_urlpatterns()