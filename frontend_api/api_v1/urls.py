from django.urls import path

from api_v1.views import (
    LoginView,
    LogoutView,
    RegisterView,
    ListBooksView,
    BorrowBookView,
    JWTRefreshView,
    RetrieveBookView,
)


urlpatterns = [
    path("books/", ListBooksView.as_view(), name="list-books"),
    path("books/<uuid:pk>/", RetrieveBookView.as_view(), name="retrieve-book"),
    path("borrow/", BorrowBookView.as_view(), name="borrow-book"),
    path("user/register/", RegisterView.as_view(), name="register-user"),
    path("user/login/", LoginView.as_view(), name="login"),
    path("user/logout/", LogoutView.as_view(), name="logout"),
    path("user/refresh_jwt/", JWTRefreshView.as_view(), name="refresh_jwt"),
]
