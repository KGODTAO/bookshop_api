from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model
from account.models import User

admin.site.register(User)