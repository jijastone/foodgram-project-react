from rest_framework.pagination import PageNumberPagination

from foodgram.constants import PAG_LIMIT


class CustomPagination(PageNumberPagination):
    page_size = PAG_LIMIT
    page_size_query_param = 'limit'
