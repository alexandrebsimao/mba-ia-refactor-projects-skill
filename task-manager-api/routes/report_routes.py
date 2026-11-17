from flask import Blueprint
from controllers.report_controller import ReportController
from controllers.category_controller import CategoryController

report_bp = Blueprint('reports', __name__)

report_bp.route('/reports/summary', methods=['GET'])(ReportController.summary_report)
report_bp.route('/reports/user/<int:user_id>', methods=['GET'])(ReportController.user_report)

# Mantém retrocompatibilidade caso cliente acesse através de report_bp
report_bp.route('/categories', methods=['GET'])(CategoryController.get_categories)
report_bp.route('/categories', methods=['POST'])(CategoryController.create_category)
report_bp.route('/categories/<int:cat_id>', methods=['PUT'])(CategoryController.update_category)
report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])(CategoryController.delete_category)
