from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import SecSearchSerializer
from .methods.get_sec_urls import get_sec_urls, SECDataError

@api_view(['GET'])
def get_sec_files(request):
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
def update_t212(request): #WIP
    pass