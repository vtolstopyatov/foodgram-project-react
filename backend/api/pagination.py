from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Переопредлеяет название query параметра"""
    page_size_query_param = 'limit'
