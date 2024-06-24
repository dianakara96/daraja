# from django.shortcuts import render
# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from .models import MpesaRequest, MpesaResponse
# from .serializers import MpesaRequestSerializer, MpesaResponseSerializer
# import requests
# import base64
# from datetime import datetime
# from django.conf import settings
# # Create your views here.
# def home(request):
#     return render(request, 'home.html')

# @api_view(['POST'])
# def stk_push(request):
#     serializer = MpesaRequestSerializer(data=request.data)
#     if serializer.is_valid():
#         mpesa_request = serializer.save()
#         response_data = initiate_stk_push(mpesa_request)
#         mpesa_response = MpesaResponse.objects.create(
#             request=mpesa_request,
#             merchant_request_id=response_data.get('MerchantRequestID', ''),
#             checkout_request_id=response_data.get('CheckoutRequestID', ''),
#             response_code=response_data.get('ResponseCode', ''),
#             response_description=response_data.get('ResponseDescription', ''),
#             customer_message=response_data.get('CustomerMessage', '')
#         )
#         response_serializer = MpesaResponseSerializer(mpesa_response)
#         return Response(response_serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# def initiate_stk_push(mpesa_request):
#     access_token = get_access_token()
#     api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
#     headers = {
#         "Authorization": f"Bearer {access_token}"
#     }
#     payload = {
#         "BusinessShortCode": settings.MPESA_SHORTCODE,
#         "Password": generate_password(),
#         "Timestamp": datetime.now().strftime('%Y%m%d%H%M%S'),
#         "TransactionType": "CustomerPayBillOnline",
#         "Amount": float(mpesa_request.amount),  # Convert Decimal to float
#         "PartyA": mpesa_request.phone_number,
#         "PartyB": settings.MPESA_SHORTCODE,
#         "PhoneNumber": mpesa_request.phone_number,
#         "CallBackURL": "https://your-callback-url.com/callback",  # Update with your actual callback URL
#         "AccountReference": mpesa_request.account_reference,
#         "TransactionDesc": mpesa_request.transaction_desc
#     }
#     response = requests.post(api_url, json=payload, headers=headers)
#     return response.json()

# def get_access_token():
#     consumer_key = settings.MPESA_CONSUMER_KEY
#     consumer_secret = settings.MPESA_CONSUMER_SECRET
#     api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
#     response = requests.get(api_url, auth=(consumer_key, consumer_secret))
#     access_token = response.json().get('access_token')
#     return access_token

# def generate_password():
#     shortcode = settings.MPESA_SHORTCODE
#     passkey = settings.MPESA_PASSKEY
#     timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
#     data_to_encode = shortcode + passkey + timestamp
#     encoded_string = base64.b64encode(data_to_encode.encode())
#     return encoded_string.decode('utf-8')


from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import MpesaRequest, MpesaResponse
from .serializers import MpesaRequestSerializer, MpesaResponseSerializer
import requests
import base64
from datetime import datetime
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def home(request):
    return render(request, 'home.html')

@api_view(['POST'])
def stk_push(request):
    serializer = MpesaRequestSerializer(data=request.data)
    if serializer.is_valid():
        mpesa_request = serializer.save()
        response_data = initiate_stk_push(mpesa_request)
        mpesa_response = MpesaResponse.objects.create(
            request=mpesa_request,
            merchant_request_id=response_data.get('MerchantRequestID', ''),
            checkout_request_id=response_data.get('CheckoutRequestID', ''),
            response_code=response_data.get('ResponseCode', ''),
            response_description=response_data.get('ResponseDescription', ''),
            customer_message=response_data.get('CustomerMessage', '')
        )
        response_serializer = MpesaResponseSerializer(mpesa_response)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def initiate_stk_push(mpesa_request):
    access_token = get_access_token()
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": generate_password(),
        "Timestamp": datetime.now().strftime('%Y%m%d%H%M%S'),
        "TransactionType": "CustomerPayBillOnline",
        "Amount": float(mpesa_request.amount),  # Convert Decimal to float
        "PartyA": mpesa_request.phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": mpesa_request.phone_number,
        "CallBackURL": "https://your-domain.com/callback/",  # Update with your actual callback URL
        "AccountReference": mpesa_request.account_reference,
        "TransactionDesc": mpesa_request.transaction_desc
    }
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

def get_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(api_url, auth=(consumer_key, consumer_secret))
    access_token = response.json().get('access_token')
    return access_token

def generate_password():
    shortcode = settings.MPESA_SHORTCODE
    passkey = settings.MPESA_PASSKEY
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = shortcode + passkey + timestamp
    encoded_string = base64.b64encode(data_to_encode.encode())
    return encoded_string.decode('utf-8')

@csrf_exempt
@api_view(['POST'])
def mpesa_callback(request):
    callback_data = json.loads(request.body.decode('utf-8'))
    merchant_request_id = callback_data['Body']['stkCallback']['MerchantRequestID']
    checkout_request_id = callback_data['Body']['stkCallback']['CheckoutRequestID']
    result_code = callback_data['Body']['stkCallback']['ResultCode']
    result_desc = callback_data['Body']['stkCallback']['ResultDesc']

    try:
        mpesa_response = MpesaResponse.objects.get(
            merchant_request_id=merchant_request_id,
            checkout_request_id=checkout_request_id
        )
        mpesa_response.response_code = result_code
        mpesa_response.response_description = result_desc
        mpesa_response.save()

        response_serializer = MpesaResponseSerializer(mpesa_response)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    except MpesaResponse.DoesNotExist:
        return Response({"error": "MpesaResponse not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def mpesa_request_list(request):
    mpesa_requests = MpesaRequest.objects.all()
    serializer = MpesaRequestSerializer(mpesa_requests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def mpesa_response_list(request):
    mpesa_responses = MpesaResponse.objects.all()
    serializer = MpesaResponseSerializer(mpesa_responses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

