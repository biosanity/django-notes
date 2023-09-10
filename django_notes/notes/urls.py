from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.editor, name="home"),
    path('delete_note/<int:note_id>', views.delete_note, name="delete_note")
]
