"""
URL configuration for AIops project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from AIapp.views import *
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', user_login, name="user_login_url"),
    path('user_login', user_login, name="user_login_url"),
    path('admin_login', admin_login, name="admin_login_url"),
    path('register', register, name="register_url"),
    path('user_index.html', user_index, name='user_index_url'),
    path('user_upload.html', user_upload, name='user_upload_url'),
    path('user_comment.html', user_comment, name='user_comment_url'),
    path('admin_index.html', admin_index, name='admin_index_url'),
    path('login_page.html', login_page, name='login_page_url'),
    path('trace_test/',trace_test,name='trace_test_url'),
    path('show_csv_content/',show_csv_content,name='show_csv_content_url'),
    path('download/',download_csv,name='download_url')
]
