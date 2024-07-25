from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import SecSearchSerializer
from typing import TYPE_CHECKING
import logging

import ipdb

from .methods.get_sec_urls import get_sec_urls, SECDataError
from .methods.updateT212 import updateT212

from classes.users import User
from classes.portfolio import Portfolio
from master.mongoDB import mongo_client

if TYPE_CHECKING:
    from django.http import HttpRequest


logger = logging.getLogger('myapp')

@api_view(['GET'])
def get_sec_files(request: 'HttpRequest'):
    serializer = SecSearchSerializer(data=request.GET)
    if serializer.is_valid():
        data = serializer.validated_data
        try:
            result = get_sec_urls(**data)
            return Response(result, status=status.HTTP_200_OK)
        except SECDataError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def update_t212(request: 'HttpRequest'):
    client_id = request.COOKIES['client_id']
    logger.info(f'Update_t212 request from {client_id}')
    result = updateT212(client_id)
    return Response(result, status=status.HTTP_200_OK)

@api_view(['GET'])
def stock_history(request: 'HttpRequest'):
    client_id = request.COOKIES['client_id']
    user = User(client_id, mongo_client=mongo_client)
    user.connect_user(fast_connect=True)
    # ipdb.set_trace()
    ptf = Portfolio(mongo_client, user.ptf_ids[0])
    ptf.load()
    result = ptf.stock_history()
    print(result)
    return Response(result, status=status.HTTP_200_OK)

