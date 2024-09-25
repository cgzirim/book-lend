from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api_v1.views import (
    BookView,
    RegisterView,
    LoginView,
    LogoutView,
    ListUsersView,
    ListBorrowedBooksView,
    JWTRefreshView,
)

router = DefaultRouter()
router.register(r"books", BookView, basename="book")

urlpatterns = [
    path("", include(router.urls)),
    path("users/", ListUsersView.as_view(), name="list-users"),
    path(
        "borrowed_books/", ListBorrowedBooksView.as_view(), name="list-borrowed-books"
    ),
    path("admin/register/", RegisterView.as_view(), name="register-user"),
    path("admin/login/", LoginView.as_view(), name="login"),
    path("admin/logout/", LogoutView.as_view(), name="logout"),
    path("admin/refresh/token/", JWTRefreshView.as_view(), name="refresh_jwt"),
]
