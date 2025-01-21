from rest_framework.pagination import PageNumberPagination

class MessagePageNumberPagination(PageNumberPagination):
    page_size = 15 
    page_size_query_param = 'page_size' 
    max_page_size = 100


class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class RatingPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 100