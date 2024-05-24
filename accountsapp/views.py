from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Account, Destination
from .serializers import AccountSerializer, DestinationSerializer
import requests

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

@api_view(['GET'])
def get_destinations(request, account_id):
    try:
        account = Account.objects.get(account_id=account_id)
        destinations = account.destinations.all()
        serializer = DestinationSerializer(destinations, many=True)
        return Response(serializer.data)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def incoming_data(request):
    secret_token = request.headers.get('CL-X-TOKEN')
    if not secret_token:
        return Response({'error': 'Un Authenticate'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        account = Account.objects.get(app_secret_token=secret_token)
    except Account.DoesNotExist:
        return Response({'error': 'Un Authenticate'}, status=status.HTTP_401_UNAUTHORIZED)

    data = request.data
    for destination in account.destinations.all():
        headers = destination.headers
        method = destination.http_method
        url = destination.url

        if method == 'GET':
            response = requests.get(url, headers=headers, params=data)
        elif method in ['POST', 'PUT']:
            response = getattr(requests, method.lower())(url, headers=headers, json=data)

    return Response({'status': 'success'})
