"""
This module implements authentication and authorization features
"""
from functools import wraps
from flask import abort, request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    current_user,
    create_access_token,
    JWTManager,
)

from flask_restful import Resource
from .models.user import User
from .utils import get_current_restaurant
from werkzeug.security import check_password_hash
from .extensions import jwt


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


class LoginResource(Resource):
    def post(self):
        # Get the JSON data from the request body
        data = request.get_json()

        # Validate the login information
        email = data.get("email")
        user = User.find_by_email(email)
        password = data.get("password")
        if not user or not password:
            return {"message": "Missing username or password"}, 400

        # Check the password
        if not check_password_hash(user.password_hash, password):
            return {"message": "Invalid username or password"}, 401

        # Generate a JWT for the user identity
        access_token = create_access_token(identity=user.id)

        # Return the JWT as part of the response body
        return {"message": "Login successful", "access_token": access_token}, 200


def authenticate(email, password):
    user = User.find_by_email(email)
    if user and user.check_password(password):
        return create_access_token(identity=user.id)


def identity(payload):
    user_id = payload['identity']
    return User.find_by_id(user_id)


def authenticated_user():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            if current_user and current_user.is_activated():
                return fn(*args, **kwargs)
            return abort(403)
        return decorator
    return wrapper


def only_admin():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            if current_user and current_user.is_activated() and current_user.is_admin:
                return fn(*args, **kwargs)
            return abort(403)
        return decorator
    return wrapper


def only_manager():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            restaurant = get_current_restaurant()
            if current_user.is_activated() and ((current_user.is_admin) or current_user.is_manager_of(restaurant)):
                return fn(*args, **kwargs)
            return abort(403)
        return decorator
    return wrapper
