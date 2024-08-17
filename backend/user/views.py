import ipdb
from django.http import JsonResponse
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from admin.mongoDB import mongo_client
from classes.users import User, UserError

from .serializers import ConnectionSerializer


class Index(TemplateView):
    template_name = "login.html"


@api_view(["POST"])
def connection(request):
    # ipdb.set_trace()
    serializer = ConnectionSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        try:
            new_user = data.pop("new_user", None)
            user = User(**data, mongo_client=mongo_client)
            user.connect_user(new_user)
            token = user.generate_token(duration=20)

            original_request = request.session.get("original_request", None)
            if original_request:
                response_data = {"redirect_url": original_request}
            else:
                response_data = {"redirect_url": "http://localhost:5173/"}  # temp url
            response = JsonResponse(response_data)
            response.set_cookie(
                "token", token.get("value"), max_age=20 * 60, secure=True, httponly=True
            )
            response.set_cookie("client_id", user._id, secure=True, httponly=True)
            response.status_code = 301
            return response
        except UserError as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            print(e)
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
