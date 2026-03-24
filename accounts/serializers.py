from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import NotificationPreference, User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name',
                  'user_type', 'profile_picture', 'mobile_number', 'whatsapp_number',
                  'is_verified', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_type', 'is_verified', 'created_at', 'updated_at']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for customer registration"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name',
                  'mobile_number', 'whatsapp_number']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Validate mobile number format
        mobile_number = str(attrs.get('mobile_number', ''))
        if mobile_number and not mobile_number.startswith('+233'):
            raise serializers.ValidationError({"mobile_number": "Please use Ghana phone number format (+233...)"})
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            mobile_number=validated_data['mobile_number'],
            whatsapp_number=validated_data.get('whatsapp_number'),
            user_type='CUSTOMER',
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')
        
        attrs['user'] = user
        return attrs


class UsernameOrEmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT login serializer that accepts either username or email."""
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")

        if not username and not email:
            raise serializers.ValidationError(
                {"detail": "Provide either username or email with password."}
            )

        # Support explicit `email` field login.
        if email:
            user = User.objects.filter(email__iexact=email).first()
            attrs[self.username_field] = (
                getattr(user, self.username_field) if user else email
            )
        else:
            # Support legacy `username` field carrying either username or email.
            user = User.objects.filter(email__iexact=username).first()
            attrs[self.username_field] = (
                getattr(user, self.username_field) if user else username
            )

        attrs.pop("email", None)
        return super().validate(attrs)


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    current_password = serializers.CharField(required=False, write_only=True)
    old_password = serializers.CharField(required=False, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(required=False, write_only=True)
    new_password2 = serializers.CharField(required=False, write_only=True)
    
    def validate(self, attrs):
        current_password = attrs.get("current_password") or attrs.get("old_password")
        confirm_new_password = attrs.get("confirm_new_password") or attrs.get("new_password2")

        if not current_password:
            raise serializers.ValidationError(
                {"current_password": "Current password is required."}
            )
        if not confirm_new_password:
            raise serializers.ValidationError(
                {"confirm_new_password": "Please confirm the new password."}
            )
        if attrs["new_password"] != confirm_new_password:
            raise serializers.ValidationError(
                {"confirm_new_password": "New password fields didn't match."}
            )

        attrs["current_password"] = current_password
        attrs["confirm_new_password"] = confirm_new_password
        return attrs
    
    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'mobile_number', 
                  'whatsapp_number', 'profile_picture']
    
    def validate_mobile_number(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(mobile_number=value).exists():
            raise serializers.ValidationError("This mobile number is already in use.")
        return value


class ProfileContractSerializer(serializers.ModelSerializer):
    """Profile read contract used by frontend profile settings."""

    location = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "mobile_number",
            "whatsapp_number",
            "location",
            "profile_picture",
            "profile_picture_url",
            "is_verified",
            "is_active",
            "user_type",
        ]
        read_only_fields = ["id", "is_verified", "is_active", "user_type", "profile_picture_url"]

    def get_location(self, obj):
        customer_profile = getattr(obj, "customer_profile", None)
        if customer_profile is None:
            return None
        return customer_profile.location

    def get_profile_picture_url(self, obj):
        if not obj.profile_picture:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.profile_picture.url)
        return obj.profile_picture.url


class ProfileContractUpdateSerializer(serializers.ModelSerializer):
    """Profile update contract for editable user settings fields."""

    location = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "mobile_number",
            "whatsapp_number",
            "profile_picture",
            "location",
        ]

    def validate_username(self, value):
        user = self.context["request"].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("This username is already in use.")
        return value

    def validate_mobile_number(self, value):
        user = self.context["request"].user
        if User.objects.exclude(pk=user.pk).filter(mobile_number=value).exists():
            raise serializers.ValidationError("This mobile number is already in use.")
        return value

    def update(self, instance, validated_data):
        location = validated_data.pop("location", None)
        user = super().update(instance, validated_data)

        if location is not None:
            from customers.models import Customer

            customer_profile, _ = Customer.objects.get_or_create(
                user=user,
                defaults={"location": location or ""},
            )
            customer_profile.location = location or ""
            customer_profile.save(update_fields=["location", "updated_at"])

        return user


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            "order_updates",
            "price_alerts",
            "announcements",
            "whatsapp_notifications",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]


class ProfilePictureUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["profile_picture"]
