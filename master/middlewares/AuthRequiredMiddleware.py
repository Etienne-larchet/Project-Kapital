import logging
from django.shortcuts import redirect
from django.urls import reverse
from master.mongodb import mongo_client
from datetime import datetime
from typing import TYPE_CHECKING
from django.utils.deprecation import MiddlewareMixin
from classes.users import User
from django.contrib import messages
from bson import ObjectId
from urllib.parse import urlencode

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def save_request(request: 'HttpRequest') -> None:
    if request.method == 'GET':
        base_url = request.path
        query_params = request.GET.dict()
        original_request = f'{base_url}?{urlencode(query_params)}'
    else:
        logging.warning(f"Method '{request.method}' not supported in redirection")
    request.session['original_request'] = original_request


class AuthRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request: 'HttpRequest'):
        # Skip authentication for login and static pages
        if request.path.startswith('/login'):
            return None  # Return None to continue processing the request
        
        is_authenticated = False
        token = request.COOKIES.get('token', None)
        client_id = request.COOKIES.get('client_id', None)
        if token:
            identification = mongo_client.users.tokens.find_one({"token.value": token})
            if identification:
                expiration = identification['token']['expiration']
                if expiration >= datetime.now() and identification['_id'] == ObjectId(client_id):
                    is_authenticated = True
                else:
                    logging.warning(f"Token expired for user {client_id}. Redirecting to login.")
                    messages.error(request, "Your session has expired. Please log in again.")
            else:
                logging.warning("Token not found in database. Redirecting to login.")
                messages.error(request, "Invalid token. Please log in again.")
        else:
            logging.warning("No token found in request. Redirecting to login.")
            messages.error(request, "You are not logged in. Please log in to continue.")
            
        if not is_authenticated:
            save_request(request)
            return redirect(reverse('user:index'))  # Redirect unauthenticated users

    def process_response(self, request: 'HttpRequest', response: 'HttpResponse'):
        # Skip token update for login and static pages
        if request.path.startswith('/login'):
            return response
        
        # Update the token if the response status is 2xx or 3xx
        if response.status_code // 100 in [2, 3]:
            old_token_value = request.COOKIES.get('token')
            if old_token_value:
                new_token = User.generate_token(duration=20)
                mongo_client.users.tokens.find_one_and_update(
                    {'token.value': old_token_value}, 
                    {'$set': {'token': new_token}}
                )
                response.set_cookie(
                    'token', new_token.get('value'), 
                    max_age=int(120*60), # higher number than internal token duration to inform the user of its deconnexion
                    secure=True, httponly=True
                )
        return response