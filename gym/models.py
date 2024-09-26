from django.db import models
from django.contrib.auth.models import User





class GymData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gym_name = models.CharField(max_length=50)
    gym_address = models.TextField()
    gym_phone = models.CharField(max_length=15)
    gym_website = models.URLField()
    gym_logo = models.ImageField(upload_to="gym_logo/")
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.gym_name

    class Meta:
        verbose_name = "Gym Data"
        verbose_name_plural = "Gym Data"


class Member(models.Model):
    gym = models.ForeignKey(GymData, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)
    created_date = models.DateField(auto_now_add=True)
    join_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Member"
        verbose_name_plural = "Members"



class Plan(models.Model):
    gym = models.ForeignKey(GymData, on_delete=models.CASCADE)
    plan_name = models.CharField(max_length=50)
    plan_description = models.TextField()
    plan_price = models.DecimalField(max_digits=10, decimal_places=2)
    plan_duration = models.PositiveIntegerField()
    plan_duration_type = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.plan_name

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Plans"


class Membership(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.member.first_name} {self.member.last_name}"

    class Meta:
        verbose_name = "Membership"
        verbose_name_plural = "Memberships"

    
