"""
This module implements authentication and authorization features
"""
from functools import wraps

from flask import abort, request
from flask_jwt import current_identity, _jwt_required
from flask_jwt_extended import create_access_token
from flask_restful import Resource

from .models.user import User
from .utils import get_current_restaurant


class LoginResource(Resource):
    def post(self):
        # Get the JSON data from the request body
        data = request.get_json()

        # Validate the login information
        email = data.get("email")
        username = User.find_by_email(email)
        password = data.get("password")
        if not username or not password:
            return {"message": "Missing username or password"}, 400
        # Replace this with your own logic or database query
        user = User.find_by_username(username)
        if not user or user.password != password:
            return {"message": "Invalid username or password"}, 401

        # Generate a JWT for the user identity
        access_token = create_access_token(identity=username)

        # Return the JWT as part of the response body
        return {"message": "Login successful", "access_token": access_token}, 200


def authenticate(email, password):
    user = User.find_by_email(email)
    if user and user.check_password(password):
        return user


def identity(payload):
    user_id = payload['identity']
    user = User.find_by_id(user_id)
    return user


def authenticated_user():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            _jwt_required(None)
            if current_identity.is_activated():
                return fn(*args, **kwargs)
            return abort(403)
        return decorator
    return wrapper


def only_admin():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            _jwt_required(None)
            if current_identity.is_activated() and current_identity.is_admin:
                return fn(*args, **kwargs)
            return abort(403)
        return decorator
    return wrapper


def only_manager():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            _jwt_required(None)
            restaurant = get_current_restaurant()
            if current_identity.is_activated() and \
                    ((current_identity.is_admin) or
                     current_identity.is_manager_of(restaurant)):
                return fn(*args, **kwargs)
            return abort(403)
        return decorator
    return wrapper
