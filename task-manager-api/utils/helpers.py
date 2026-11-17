from datetime import datetime, timezone
import logging
import re
import uuid

logger = logging.getLogger(__name__)

VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
VALID_ROLES = ['user', 'admin', 'manager']
MAX_TITLE_LENGTH = 200
MIN_TITLE_LENGTH = 3
MIN_PASSWORD_LENGTH = 4
DEFAULT_PRIORITY = 3
DEFAULT_COLOR = '#000000'


def format_date(date_obj):
    if date_obj:
        return str(date_obj)
    return None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    if not isinstance(email, str):
        return False
    return bool(re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email))


def sanitize_string(text):
    if isinstance(text, str):
        return text.strip()
    return text


def generate_id():
    return str(uuid.uuid4())


def log_action(action, details=None):
    timestamp = datetime.now(timezone.utc).isoformat()
    logger.info("[%s] ACTION: %s | DETAILS: %s", timestamp, action, details)


def parse_date(date_string):
    if not isinstance(date_string, str):
        return None
    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    return None


def is_valid_color(color):
    return bool(color and len(color) == 7 and color[0] == '#')


def process_task_data(data, existing_task=None):
    result = {}

    if 'title' in data:
        title = data['title']
        if title:
            title = title.strip()
            if MIN_TITLE_LENGTH <= len(title) <= MAX_TITLE_LENGTH:
                result['title'] = title
            else:
                return None, f'Título deve ter entre {MIN_TITLE_LENGTH} e {MAX_TITLE_LENGTH} caracteres'
        else:
            return None, 'Título não pode ser vazio'

    if 'description' in data:
        result['description'] = data['description']

    if 'status' in data:
        if data['status'] in VALID_STATUSES:
            result['status'] = data['status']
        else:
            return None, 'Status inválido'

    if 'priority' in data:
        try:
            priority = int(data['priority'])
            if 1 <= priority <= 5:
                result['priority'] = priority
            else:
                return None, 'Prioridade deve ser entre 1 e 5'
        except (ValueError, TypeError):
            return None, 'Prioridade inválida'

    if 'due_date' in data:
        if data['due_date']:
            parsed = parse_date(data['due_date'])
            if parsed:
                result['due_date'] = parsed
            else:
                return None, 'Data inválida'
        else:
            result['due_date'] = None

    if 'tags' in data:
        tags = data['tags']
        result['tags'] = ','.join(tags) if isinstance(tags, list) else tags

    return result, None
