from django.urls import include, path
from .views import *


urlpatterns = [
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('verificate/', verificate, name='verificate'),
    path('logout/', logout_view, name='logout'),
    path('update-code/', update_code, name='update_code')
]