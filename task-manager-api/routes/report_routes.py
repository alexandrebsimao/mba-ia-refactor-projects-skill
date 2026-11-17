from flask import Blueprint
from controllers.report_controller import ReportController

report_bp = Blueprint('reports', __name__)

report_bp.route('/reports/summary', methods=['GET'])(ReportController.summary_report)
report_bp.route('/reports/user/<int:user_id>', methods=['GET'])(ReportController.user_report)
