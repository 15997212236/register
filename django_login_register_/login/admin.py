from django.contrib import admin
# admin
# python123

# Register your models here.
from . import models
admin.site.register(models.User)
admin.site.register(models.ConfirmString)