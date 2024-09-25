from django.utils import timezone
from datetime import timedelta, datetime
from drf_spectacular.utils import extend_schema
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    GenericAPIView,
)

from api_v1.filters import BookFilter
from api_v1.models import User, Book, BorrowedBook
from api_v1.serializers import (
    BookSerializer,
    BorrowedBookSerializer,
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    UserSerializer,
)


@extend_schema(tags=["Frontend_api"], summary="List all available books")
class ListBooksView(ListAPIView):
    queryset = Book.objects.filter(is_available=True)
    serializer_class = BookSerializer

    search_fields = ["title"]
    filterset_class = BookFilter
    filter_backends = [DjangoFilterBackend, SearchFilter]


@extend_schema(tags=["Frontend_api"], summary="Get a single book by its ID")
class RetrieveBookView(RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


@extend_schema(tags=["Frontend_api"], summary="Borrow book by id")
class BorrowBookView(CreateAPIView):
    permission_classes = []
    queryset = BorrowedBook.objects.all()
    serializer_class = BorrowedBookSerializer

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        book = data["book"]

        borrow_days = data.pop("days")
        due_date = timezone.now() + timedelta(days=borrow_days)

        serializer.save(due_date=due_date)

        book.is_available = False
        book.save()

        return Response(
            {"detail": "Book borrowed successfully."}, status=status.HTTP_201_CREATED
        )


sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters("password1", "password2"),
)


def get_login_data(user):
    from rest_framework_simplejwt.settings import (
        api_settings as jwt_settings,
    )

    refresh_token = RefreshToken.for_user(user)
    access_token = refresh_token.access_token

    access_token_expiration = timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME
    refresh_token_expiration = timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME

    user_serializer = UserSerializer(user)

    data = {
        "user": user_serializer.data,
        "access": str(access_token),
        "refresh": str(refresh_token),
        "access_expiration": access_token_expiration,
        "refresh_expiration": refresh_token_expiration,
    }

    return data


@extend_schema(tags=["Auth"], summary="Enroll user into the library")
class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save(is_active=True)

        login_data = get_login_data(user)

        return Response(login_data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Auth"])
class LoginView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)

        user = self.serializer.validated_data["user"]
        user.last_login = timezone.now()
        user.save()

        data = get_login_data(user)

        return Response(data, status=status.HTTP_200_OK)


@extend_schema(tags=["Auth"])
class LogoutView(GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        self.request = request
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        response = Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_200_OK,
        )

        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except KeyError:
            response.data = {
                "detail": "Refresh token was not included in request data."
            }
            response.status_code = status.HTTP_401_UNAUTHORIZED
        except (TokenError, AttributeError, TypeError) as error:
            if hasattr(error, "args"):
                if (
                    "Token is blacklisted" in error.args
                    or "Token is invalid or expired" in error.args
                ):
                    response.data = {"detail": error.args[0]}
                    response.status_code = status.HTTP_400_BAD_REQUEST
                else:
                    response.data = {"detail": "An error has occurred."}
                    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            else:
                response.data = {"detail": "An error has occurred."}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return response


@extend_schema(tags=["Auth"])
class JWTRefreshView(TokenRefreshView):
    pass
