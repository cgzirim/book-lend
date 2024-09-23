from django_filters import FilterSet

from api_v1.models import Book


class BookFilter(FilterSet):
    class Meta:
        model = Book
        fields = ["category", "publisher"]
