from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from api_v1.models import Book, BorrowedBook, User


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"


class BorrowedBookSerializer(serializers.ModelSerializer):
    days = serializers.IntegerField(write_only=True)

    class Meta:
        model = BorrowedBook
        fields = "__all__"
        read_only_fields = ["due_date"]

    def validate_days(self, days):
        if days <= 0:
            raise serializers.ValidationError("Value must be greated than 0.")

    def validate_book(self, book):
        if not book.is_available:
            raise serializers.ValidationError("This book is not available.")

        return book


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "is_active", "last_login"]


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        user.set_password(validated_data["password"])
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    password = serializers.CharField(style={"input_type": "password"})

    @staticmethod
    def validate_auth_user_status(user):
        if not user.is_active:
            msg = "User account is disabled."
            raise serializers.ValidationError(msg)

    def authenticate(self, **kwargs):
        return authenticate(self.context["request"], **kwargs)

    def get_user(self, data):
        credentials = {"email": data.get("email"), "password": data.get("password")}

        user = self.authenticate(**credentials)
        return user

    def validate(self, attrs):
        user = self.get_user(attrs)
        if not user:
            msg = "Unable to log in with provided credentials."
            raise serializers.ValidationError(msg)

        self.validate_auth_user_status(user)

        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
