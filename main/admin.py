from django.contrib import admin
from rest_framework.authtoken.admin import User

from.models import (Category, Book, Review, Order, OrderItems)
# Register your models here.


admin.site.register(Category)
admin.site.register(Book)

