'''
Продукты могут фильтроваться по категории по названию или описанию по цене ( дороже дешевле)

Заказы могут фильтроваться ( по продукту по дате по сумме )

'''
import django_filters
from django_filters.rest_framework import FilterSet

from main.models import Book, Order


class BookFilter(FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    description = django_filters.CharFilter(field_name='description', lookup_expr='icontains')
    price_from = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_to = django_filters.NumberFilter(field_name='price', lookup_expr='lte')



    class Meta:
        model = Book
        fields = ('category', 'title', 'description', 'price_from', 'price_to')


class OrderFilter(FilterSet):
    '''Фильтрация по сумме(от, до)
        По названию товару по статуса по дате'''
    total_sum_from = django_filters.NumberFilter(field_name='total_sum', lookup_expr='gte')
    total_sum_to = django_filters.NumberFilter(field_name='total_sum', lookup_expr='lte')

    created_at = django_filters.DateTimeFromToRangeFilter(field_name='created_at')
    book = django_filters.CharFilter(field_name='books__book__title', lookup_expr='icontains')
    class Meta:
        model = Order
        fields = ('total_sum_from', 'total_sum_to', 'created_at', 'book')

