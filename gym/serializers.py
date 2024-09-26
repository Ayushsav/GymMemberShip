# gym/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import GymData

class GymOwnerRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    gym_name = serializers.CharField(max_length=50, required=True)
    gym_address = serializers.CharField(required=True)
    gym_phone = serializers.CharField(max_length=15, required=True)
    gym_website = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name',
                  'gym_name', 'gym_address','gym_phone', 'gym_website')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()

        # Create GymData linked to the user
        GymData.objects.create(
            user=user,
            gym_name=validated_data['gym_name'],
            gym_address=validated_data['gym_address'],
            gym_phone=validated_data['gym_phone'],
            gym_website=validated_data.get('gym_website', ''),
        )
        return user

class GymOwnerLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")


from .models import Member

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'created_date', 'join_date', 'is_active']
# gym/serializers.py
from rest_framework import serializers
from .models import Plan

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'plan_name', 'plan_description', 'plan_price', 'plan_duration', 'plan_duration_type', 'is_active']
# gym/serializers.py
# gym/serializers.py
from rest_framework import serializers
from .models import Membership

class MembershipSerializer(serializers.ModelSerializer):
    end_date = serializers.DateTimeField(read_only=True)  # Change to DateTimeField if needed

    class Meta:
        model = Membership
        fields = ['id', 'member', 'plan', 'start_date', 'end_date', 'is_active']


from rest_framework import serializers
from .models import GymData

class GymDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymData
        fields = ['gym_name', 'gym_address', 'gym_phone', 'gym_website', 'gym_logo', 'created_date']
