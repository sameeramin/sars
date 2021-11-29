"""
URLs file for articles app and default route of this project will be from
this app
"""

from django.urls import path

from . import views
from .middlewares import auth_middleware

urlpatterns = [
    path('', auth_middleware(views.index), name='index'),
    path('add_article/', auth_middleware(views.add_article), name='add_article'),
    path('articles/', auth_middleware(views.articles), name='articles'),
    path('manage_users/', auth_middleware(views.manage_users), name='manage_users'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
]
