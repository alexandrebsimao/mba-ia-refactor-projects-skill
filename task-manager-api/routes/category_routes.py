from flask import Blueprint
from controllers.category_controller import CategoryController

category_bp = Blueprint('categories', __name__)

category_bp.route('/categories', methods=['GET'])(CategoryController.get_categories)
category_bp.route('/categories', methods=['POST'])(CategoryController.create_category)
category_bp.route('/categories/<int:cat_id>', methods=['PUT'])(CategoryController.update_category)
category_bp.route('/categories/<int:cat_id>', methods=['DELETE'])(CategoryController.delete_category)
