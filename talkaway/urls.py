from django.contrib import admin
from django.urls import (
    path,
    include
)
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('gcp/', include('gcp.urls')),
    path('gpt/', include('gpt.urls')),
    path('api-auth/', include('rest_framework.urls'))
]


drf_spectacular_urlpatterns = [
    path(
        'schema/',
        SpectacularAPIView.as_view(),
        name='schema'
    ),
    path(
        'swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
    path(
        'redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),
]

urlpatterns.extend(drf_spectacular_urlpatterns)
urlpatterns.extend(staticfiles_urlpatterns())
