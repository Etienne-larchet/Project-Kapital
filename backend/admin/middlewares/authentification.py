import logging
from datetime import datetime
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from bson import ObjectId
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.urls.exceptions import Resolver404

from admin.mongoDB import mongo_client
from classes.users import User

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("myapp")


def save_request(request: "HttpRequest") -> None:
    if request.method == "GET":
        base_url = request.path
        query_params = request.GET.dict()
        original_request = f"{base_url}?{urlencode(query_params)}"
    else:
        logger.warning(f"Method '{request.method}' not supported in redirection")
    request.session["original_request"] = original_request


def valid_path(path: str) -> bool:
    try:
        resolve(path)
        return True
    except Resolver404:
        return False


class AuthentificationMiddleware:
    WHITELISTED_PATHS = ["/login", "/favicon.ico"]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        response = self.process_response(request, response)
        return response

    def process_request(self, request: "HttpRequest"):
        if any(request.path.startswith(path) for path in self.WHITELISTED_PATHS):
            return None

        is_authenticated = False
        token = request.COOKIES.get("token", None)
        client_id = request.COOKIES.get("client_id", None)
        if token:
            identification = mongo_client.users.tokens.find_one({"token.value": token})
            if identification:
                expiration = identification["token"]["expiration"]
                if expiration >= datetime.now() and identification["_id"] == ObjectId(
                    client_id
                ):
                    is_authenticated = True
                else:
                    logger.warning(
                        f"Token expired for user {client_id}. Redirecting to login."
                    )
                    messages.error(
                        request, "Your session has expired. Please log in again."
                    )
            else:
                logger.warning("Token not found in database. Redirecting to login.")
                messages.error(request, "Invalid token. Please log in again.")
        else:
            logger.warning("No token found in request. Redirecting to login.")
            messages.error(request, "You are not logged in. Please log in to continue.")

        if not is_authenticated:
            if valid_path(request.path):
                save_request(request)
            return redirect(reverse("user:index"))  # Redirect unauthenticated users

    def process_response(self, request: "HttpRequest", response: "HttpResponse"):
        if any(request.path.startswith(path) for path in self.WHITELISTED_PATHS):
            return response

        if response.status_code // 100 in [2, 3]:
            old_token_value = request.COOKIES.get("token")
            if old_token_value:
                new_token = User.generate_token(duration=60)
                mongo_client.users.tokens.find_one_and_update(
                    {"token.value": old_token_value}, {"$set": {"token": new_token}}
                )
                response.set_cookie(
                    "token",
                    new_token.get("value"),
                    max_age=int(
                        360 * 60
                    ),  # higher number than internal token duration to inform the user of its deconnexion
                    secure=True,
                    httponly=True,
                )
        return response
