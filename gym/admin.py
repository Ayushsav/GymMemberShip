from django.contrib import admin
from .models import GymData, Member, Plan, Membership
# Register your models here.

admin.site.register(GymData)
admin.site.register(Member)
admin.site.register(Plan)
admin.site.register(Membership)