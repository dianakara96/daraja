from django.urls import path
from .views import home, stk_push, mpesa_callback, mpesa_request_list, mpesa_response_list

urlpatterns = [
    path('', home, name='home'),
    path('stk-push/', stk_push, name='stk-push'),
    path('callback/', mpesa_callback, name='mpesa-callback'),
    path('mpesa-requests/', mpesa_request_list, name='mpesa-request-list'),
    path('mpesa-responses/', mpesa_response_list, name='mpesa-response-list'),
]
