# backend/route/auth_routes.py
"""
Authentication routes.
Handles user registration, login, token refresh, and logout.
"""

from flask import Blueprint, request, jsonify, current_app
from backend.controller.auth_controller import AuthController
from backend.utils.exceptions import ValidationError, AuthenticationError, AppException

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
auth_controller = AuthController()


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    ---
    Request Body:
        name: str
        email: str
        password: str
        password_confirm: str
    Response:
        user: object
        token: str
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        result = auth_controller.register(data)
        return jsonify(result), 201

    except ValidationError as e:
        return jsonify({'error': e.message, 'details': e.details}), 400
    except AppException as e:
        return jsonify({'error': e.message}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in register: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return token.
    ---
    Request Body:
        email: str
        password: str
    Response:
        user: object
        token: str
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        result = auth_controller.login(data)
        return jsonify(result), 200

    except ValidationError as e:
        return jsonify({'error': e.message, 'details': e.details}), 400
    except AuthenticationError as e:
        return jsonify({'error': e.message}), 401
    except AppException as e:
        return jsonify({'error': e.message}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in login: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """
    Refresh an existing token.
    ---
    Request Body:
        token: str
    Response:
        token: str
    """
    try:
        data = request.get_json()
        if not data or 'token' not in data:
            return jsonify({'error': 'Token is required'}), 400

        result = auth_controller.refresh_token(data['token'])
        return jsonify(result), 200

    except AuthenticationError as e:
        return jsonify({'error': e.message}), 401
    except AppException as e:
        return jsonify({'error': e.message}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in refresh: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout user (client-side token discard).
    """
    try:
        # In stateless JWT, logout is client-side.
        # This endpoint can be used to invalidate token if needed.
        return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
    except Exception as e:
        current_app.logger.error(f"Unexpected error in logout: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Get current user from token.
    ---
    Headers:
        Authorization: Bearer <token>
    Response:
        user: object
    """
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header required'}), 401

        token = auth_header.split(' ')[1]
        result = auth_controller.get_current_user(token)
        return jsonify(result), 200

    except AuthenticationError as e:
        return jsonify({'error': e.message}), 401
    except AppException as e:
        return jsonify({'error': e.message}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in get_current_user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500