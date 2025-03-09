from flask import request, jsonify
from functools import wraps
import jwt
from config import Config

JWT_SECRET_KEY = Config.JWT_SECRET_KEY

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is missing'
            }), 401

        try:
            # Decode token
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            current_user = {'id': data['user_id']}
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token has expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Token is invalid'
            }), 401

        return f(current_user, *args, **kwargs)

    return decorated

def get_user_id_from_token(token):
    try:
        data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return data.get("user_id")
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
