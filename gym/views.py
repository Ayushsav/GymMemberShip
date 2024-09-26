# gym/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import GymOwnerRegisterSerializer, GymOwnerLoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # You can extract the access token if needed
        access_token = request.data.get("access", None)
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate the refresh token
            validated_data = self.get_serializer(data=request.data)
            validated_data.is_valid(raise_exception=True)

            # Get a new access token
            new_access_token = validated_data.validated_data['access']

            return Response({
                "access": new_access_token,
                "refresh": refresh_token  # You can choose to return the same refresh token
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class GymOwnerRegisterView(generics.CreateAPIView):
    serializer_class = GymOwnerRegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Gym Owner registered successfully!"}, status=status.HTTP_201_CREATED)

class GymOwnerLoginView(generics.GenericAPIView):
    serializer_class = GymOwnerLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


# gym/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Member, GymData
from .serializers import MemberSerializer

class MemberViewSet(viewsets.ModelViewSet):
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter members to ensure the logged-in gym owner can only manage their members
        return Member.objects.filter(gym__user=self.request.user)

    def perform_create(self, serializer):
        # Ensure the member is added to the gym owned by the authenticated user
        gym = GymData.objects.get(user=self.request.user)
        serializer.save(gym=gym)

    def destroy(self, request, *args, **kwargs):
        # Ensure only the owner of the gym can delete the member
        member = self.get_object()
        if member.gym.user != request.user:
            return Response({"detail": "Not authorized to delete this member."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Ensure only the owner of the gym can update the member
        member = self.get_object()
        if member.gym.user != request.user:
            return Response({"detail": "Not authorized to update this member."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    def partial_update(self, request, *args, **kwargs):
        # Partial update allows updating only specified fields
        member = self.get_object()
        if member.gym.user != request.user:
            return Response({"detail": "Not authorized to update this member."}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

# gym/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Plan, GymData
from .serializers import PlanSerializer

class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter plans so that the logged-in gym owner can only manage their own plans
        return Plan.objects.filter(gym__user=self.request.user)

    def perform_create(self, serializer):
        # Ensure the plan is added to the gym owned by the authenticated user
        gym = GymData.objects.get(user=self.request.user)
        serializer.save(gym=gym)

    def destroy(self, request, *args, **kwargs):
        # Ensure only the owner of the gym can delete the plan
        plan = self.get_object()
        if plan.gym.user != request.user:
            return Response({"detail": "Not authorized to delete this plan."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Ensure only the owner of the gym can update the plan
        plan = self.get_object()
        if plan.gym.user != request.user:
            return Response({"detail": "Not authorized to update this plan."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        # Partial update allows updating only specified fields
        plan = self.get_object()
        if plan.gym.user != request.user:
            return Response({"detail": "Not authorized to update this plan."}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

# views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Membership, Member, Plan
from .serializers import MembershipSerializer
from rest_framework.decorators import action

class MembershipViewSet(viewsets.ModelViewSet):
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Allow only the logged-in gym owner's memberships
        return Membership.objects.filter(member__gym__user=self.request.user)

    def perform_create(self, serializer):
        member_id = self.request.data.get('member')
        plan_id = self.request.data.get('plan')

        try:
            member = Member.objects.get(id=member_id, gym__user=self.request.user)
            plan = Plan.objects.get(id=plan_id, gym=member.gym)

            # Calculate end_date based on the plan duration and type
            now = timezone.now()
            end_date = self.calculate_end_date(now, plan)

            serializer.save(member=member, plan=plan, end_date=end_date)
        except Member.DoesNotExist:
            raise serializers.ValidationError("Member does not exist or does not belong to your gym.")
        except Plan.DoesNotExist:
            raise serializers.ValidationError("Plan does not exist or does not belong to your gym.")

    def calculate_end_date(self, start_date, plan):
        """Calculate the end date based on the plan's duration."""
        if plan.plan_duration_type.lower() == 'month':
            return start_date + timedelta(days=plan.plan_duration * 30)
        elif plan.plan_duration_type.lower() == 'day':
            return start_date + timedelta(days=plan.plan_duration)
        elif plan.plan_duration_type.lower() == 'year':
            return start_date + timedelta(days=plan.plan_duration * 365)
        else:
            raise ValueError("Invalid plan duration type.")

    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        """Renew the membership, extending the duration or changing the plan."""
        membership = self.get_object()  # Get the membership instance
        now = timezone.now()

        # Check if the membership is expired
        if membership.end_date >= now:
            # Membership is still active, extend the duration
            if 'new_plan_id' in request.data:
                new_plan_id = request.data['new_plan_id']
                try:
                    new_plan = Plan.objects.get(id=new_plan_id, gym=membership.member.gym)
                    membership.plan = new_plan  # Update the plan if provided
                except Plan.DoesNotExist:
                    return Response({"error": "New plan not found."}, status=status.HTTP_404_NOT_FOUND)

            # Reset the start date and extend the end date based on the current or new plan
            membership.start_date = now  # Reset start date to current date
            membership.end_date = self.calculate_end_date(now, membership.plan)
        else:
            # Membership is expired; renew it with the current or a new plan
            new_plan_id = request.data.get("new_plan_id", None)

            if new_plan_id:
                try:
                    new_plan = Plan.objects.get(id=new_plan_id, gym=membership.member.gym)
                    membership.plan = new_plan  # Update the plan
                except Plan.DoesNotExist:
                    return Response({"error": "New plan not found."}, status=status.HTTP_404_NOT_FOUND)

            # Renew the membership
            membership.start_date = now  # Reset start date to current date
            membership.end_date = self.calculate_end_date(now, membership.plan)

        membership.is_active = True  # Ensure the membership is marked active
        membership.save()  # Save the updated membership

        return Response(MembershipSerializer(membership).data, status=status.HTTP_200_OK)
    def single_member(self, request, pk=None):
        """Retrieve a single member's details."""
        member = Member.objects.get(id=pk, gym__user=request.user)
        serializer = MemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #expired membership list
    @action(detail=False, methods=['get'], url_path='due')
    def due_memberships(self, request):
        """Retrieve due memberships for the gym owner."""
        now = timezone.now()
        due_memberships = self.get_queryset().filter(end_date__lt=now, is_active=True)

        serializer = self.get_serializer(due_memberships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



from rest_framework import generics, permissions
from .models import GymData
from .serializers import GymDataSerializer

class GymOwnerProfileView(generics.RetrieveAPIView):
    serializer_class = GymDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Retrieve the GymData instance associated with the authenticated user
        return GymData.objects.get(user=self.request.user)
