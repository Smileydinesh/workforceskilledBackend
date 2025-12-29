from rest_framework.pagination import PageNumberPagination

class LiveWebinarPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"  # optional
    max_page_size = 50
