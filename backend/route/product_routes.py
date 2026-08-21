# backend/route/product_routes.py
"""
Product routes.
Handles CRUD operations for products.
"""

from flask import Blueprint, request, jsonify, current_app
from backend.controller.product_controller import ProductController
from backend.middleware.auth_middleware import token_required
from backend.utils.exceptions import ValidationError, NotFoundError, AppException

product_bp = Blueprint('product', __name__, url_prefix='/api/products')
product_controller = ProductController()


@product_bp.route('/', methods=['POST'])
@token_required
def create_product(current_user):
    """
    Create a new product.
    ---
    Request Body:
        description: str
        price: float
        quantity_available: int
    Response:
        product: object
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        result = product_controller.create_product(data, user_id=current_user['id'])
        return jsonify(result), 201

    except ValidationError as e:
        return jsonify({'error': e.message, 'details': e.details}), 400
    except AppException as e:
        return jsonify({'error': e.message}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in create_product: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@product_bp.route('/', methods=['GET'])
@token_required
def list_products(current_user):
    """
    List products (optionally filter by user).
    ---
    Query Parameters:
        user_id: int (optional)
    Response:
        products: list
        count: int
    """
    try:
        user_id = request.args.get('user_id', type=int)
        result = product_controller.list_products(user_id=user_id)
        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Unexpected error in list_products: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@product_bp.route('/<int:product_id>', methods=['GET'])
@token_required
def get_product(current_user, product_id):
    """
    Get a single product by ID.
    ---
    Response:
        product: object
    """
    try:
        result = product_controller.get_product(product_id)
        return jsonify(result), 200

    except NotFoundError as e:
        return jsonify({'error': e.message}), 404
    except AppException as e:
        return jsonify({'error': e.message}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in get_product: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@product_bp.route('/<int:product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    """
    Update an existing product.
    ---
    Request Body:
        description: str (optional)
        price: float (optional)
        quantity_available: int (optional)
    Response:
        product: object
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        result = product_controller.update_product(product_id, data, user_id=current_user['id'])
        return jsonify(result), 200

    except NotFoundError as e:
        return jsonify({'error': e.message}), 404
    except ValidationError as e:
        return jsonify({'error': e.message, 'details': e.details}), 400
    except AppException as e:
        return jsonify({'error': e.message}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in update_product: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@product_bp.route('/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    """
    Delete a product.
    ---
    Response:
        message: str
    """
    try:
        result = product_controller.delete_product(product_id, user_id=current_user['id'])
        return jsonify(result), 200

    except NotFoundError as e:
        return jsonify({'error': e.message}), 404
    except AppException as e:
        return jsonify({'error': e.message}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in delete_product: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@product_bp.route('/<int:product_id>/check-stock', methods=['GET'])
@token_required
def check_stock(current_user, product_id):
    """
    Check if requested quantity is available.
    ---
    Query Parameters:
        quantity: int
    Response:
        product_id: int
        available: bool
        stock: int
        requested: int
    """
    try:
        requested = request.args.get('quantity', type=int)
        if not requested:
            return jsonify({'error': 'quantity query parameter is required'}), 400

        result = product_controller.check_stock(product_id, requested)
        return jsonify(result), 200

    except NotFoundError as e:
        return jsonify({'error': e.message}), 404
    except AppException as e:
        return jsonify({'error': e.message}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in check_stock: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500