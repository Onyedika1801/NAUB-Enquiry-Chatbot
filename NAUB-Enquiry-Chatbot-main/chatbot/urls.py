from django.urls import path
from . import views

# ADD THIS LINE TO FIX THE ERROR:
app_name = 'chatbot'

urlpatterns = [
    path('', views.index, name='index'),
    path('new-chat/', views.clear_session, name='clear_session'),
]
