# backend/route/order_routes.py
"""
Order routes.
Handles order creation, item management, status updates, and queries.
"""

from flask import Blueprint, request, jsonify, current_app
from backend.controller.order_controller import OrderController
from backend.middleware.auth_middleware import token_required
from backend.utils.exceptions import (
    ValidationError,
    NotFoundError,
    BusinessRuleError,
    StateError,
    AppException
)

order_bp = Blueprint('order', __name__, url_prefix='/api/orders')
order_controller = OrderController()


@order_bp.route('/', methods=['POST'])
@token_required
def create_order(current_user):
    """
    Create a new order.
    ---
    Request Body:
        customer: str
        items: list of {product_id, quantity}
    Response:
        order: object
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        result = order_controller.create_order(data, user_id=current_user['id'])
        return jsonify(result), 201

    except ValidationError as e:
        return jsonify({'error': e.message, 'details': e.details}), 400
    except BusinessRuleError as e:
        return jsonify({'error': e.message, 'details': e.details}), 400
    except AppException as e:
        return jsonify({'error': e.message}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in create_order: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@order_bp.route('/', methods=['GET'])
@token_required
def list_orders(current_user):
    """
    List orders (optionally filter by user and status).
    ---
    Query Parameters:
        user_id: int (optional)
        status: str (optional)
    Response:
        orders: list
        count: int
    """
    try:
        user_id = request.args.get('user_id', type=int)
        status = request.args.get('status')
        result = order_controller.list_orders(user_id=user_id, status=status)
        return jsonify(result), 200

    except ValidationError as e:
        return jsonify({'error': e.message, 'details': e.details}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in list_orders: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@order_bp.route('/<int:order_id>', methods=['GET'])
@token_required
def get_order(current_user, order_id):
    """
    Get a single order by ID.
    ---
    Response:
        order: object
    """
    try:
        result = order_controller.get_order(order_id)
        return jsonify(result), 200

    except NotFoundError as e:
        return jsonify({'error': e.message}), 404
    except AppException as e:
        return jsonify({'error': e.message}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in get_order: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@order_bp.route('/<int:order_id>/items', methods=['POST'])
@token_required
def add_item_to_order(current_user, order_id):
    """
    Add an item to an existing order.
    ---
    Request Body:
        product_id: int
        quantity: int
    Response:
        order: object
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        result = order_controller.add_item_to_order(order_id, data, user_id=current_user['id'])
        return jsonify(result), 200

    except NotFoundError as e:
        return jsonify({'error': e.message}), 404
    except ValidationError as e:
        return jsonify({'error': e.message, 'details': e.details}), 400
    except StateError as e:
        return jsonify({'error': e.message, 'details': e.details}), 400
    except BusinessRuleError as e:
        return jsonify({'error': e.message, 'details': e.details}), 400
    except AppException as e:
        return jsonify({'error': e.message}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in add_item_to_order: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@order_bp.route('/<int:order_id>/status', methods=['PATCH'])
@token_required
def update_order_status(current_user, order_id):
    """
    Update the status of an order.
    ---
    Request Body:
        status: str
    Response:
        order: object
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        result = order_controller.update_order_status(order_id, data, user_id=current_user['id'])
        return jsonify(result), 200

    except NotFoundError as e:
        return jsonify({'error': e.message}), 404
    except ValidationError as e:
        return jsonify({'error': e.message, 'details': e.details}), 400
    except StateError as e:
        return jsonify({'error': e.message, 'details': e.details}), 400
    except AppException as e:
        return jsonify({'error': e.message}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in update_order_status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@order_bp.route('/<int:order_id>/total', methods=['GET'])
@token_required
def calculate_order_total(current_user, order_id):
    """
    Calculate and return the total of an order.
    ---
    Response:
        order_id: int
        total: float
    """
    try:
        result = order_controller.calculate_order_total(order_id, user_id=current_user['id'])
        return jsonify(result), 200

    except NotFoundError as e:
        return jsonify({'error': e.message}), 404
    except AppException as e:
        return jsonify({'error': e.message}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in calculate_order_total: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@order_bp.route('/<int:order_id>', methods=['DELETE'])
@token_required
def delete_order(current_user, order_id):
    """
    Delete/cancel an order (only if in created/processing state).
    ---
    Response:
        message: str
    """
    try:
        result = order_controller.delete_order(order_id, user_id=current_user['id'])
        return jsonify(result), 200

    except NotFoundError as e:
        return jsonify({'error': e.message}), 404
    except StateError as e:
        return jsonify({'error': e.message, 'details': e.details}), 400
    except AppException as e:
        return jsonify({'error': e.message}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in delete_order: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500