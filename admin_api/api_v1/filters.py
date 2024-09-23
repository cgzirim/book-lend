from django_filters import FilterSet, CharFilter

from api_v1.models import Book


class BookFilter(FilterSet):
    category = CharFilter(field_name="category", lookup_expr="iexact")
    publisher = CharFilter(field_name="publisher", lookup_expr="iexact")

    class Meta:
        model = Book
        fields = ["category", "publisher", "is_available"]
