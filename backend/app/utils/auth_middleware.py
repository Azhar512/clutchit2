from flask import request, jsonify, g
from functools import wraps
import jwt
from  config import Config

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

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({"error": "Authentication required"}), 401

        try:
            # Decode token
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            g.user_id = data['user_id']
        except:
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # This should be implemented after auth_required
        # It assumes g.user_id is set by auth_required
        if not hasattr(g, 'user_id'):
            return jsonify({"error": "Authentication required"}), 401
        
        # Here you would check if the user is an admin
        # For example, using your User model
        from  app.models.user import User
        user = User.get_by_id(g.user_id)
        
        if not user or not user.is_admin:
            return jsonify({"error": "Admin privileges required"}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def get_user_id_from_token(token):
    try:
        data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return data.get("user_id")
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token