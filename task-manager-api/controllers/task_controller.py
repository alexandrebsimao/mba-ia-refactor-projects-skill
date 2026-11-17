from flask import request, jsonify
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload
from database import db
from models.task import Task
from models.user import User
from models.category import Category

class TaskController:
    @staticmethod
    def get_tasks():
        tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
        now = datetime.now()

        result = []
        for t in tasks:
            task_data = t.to_dict()
            is_overdue = False
            if t.due_date:
                due = t.due_date.replace(tzinfo=None) if t.due_date.tzinfo else t.due_date
                if due < now and t.status not in ('done', 'cancelled'):
                    is_overdue = True

            task_data['overdue'] = is_overdue
            task_data['user_name'] = t.user.name if t.user else None
            task_data['category_name'] = t.category.name if t.category else None
            result.append(task_data)

        return jsonify(result), 200

    @staticmethod
    def get_task(task_id):
        task = db.session.get(Task, task_id)
        if not task:
            return jsonify({'error': 'Task não encontrada'}), 404

        data = task.to_dict()
        now = datetime.now()
        is_overdue = False
        if task.due_date:
            due = task.due_date.replace(tzinfo=None) if task.due_date.tzinfo else task.due_date
            if due < now and task.status not in ('done', 'cancelled'):
                is_overdue = True

        data['overdue'] = is_overdue
        return jsonify(data), 200

    @staticmethod
    def create_task():
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados inválidos'}), 400

        title = data.get('title')
        if not title:
            return jsonify({'error': 'Título é obrigatório'}), 400
        title = title.strip()
        if len(title) < 3:
            return jsonify({'error': 'Título muito curto'}), 400
        if len(title) > 200:
            return jsonify({'error': 'Título muito longo'}), 400

        description = data.get('description', '')
        status = data.get('status', 'pending')
        priority = data.get('priority', 3)
        user_id = data.get('user_id')
        category_id = data.get('category_id')
        due_date = data.get('due_date')
        tags = data.get('tags')

        if status not in ['pending', 'in_progress', 'done', 'cancelled']:
            return jsonify({'error': 'Status inválido'}), 400

        try:
            priority = int(priority)
            if priority < 1 or priority > 5:
                return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Prioridade inválida'}), 400

        if user_id:
            user = db.session.get(User, user_id)
            if not user:
                return jsonify({'error': 'Usuário não encontrado'}), 404

        if category_id:
            cat = db.session.get(Category, category_id)
            if not cat:
                return jsonify({'error': 'Categoria não encontrada'}), 404

        task = Task()
        task.title = title
        task.description = description
        task.status = status
        task.priority = priority
        task.user_id = user_id
        task.category_id = category_id

        if due_date:
            try:
                task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400

        if tags:
            task.tags = ','.join(tags) if isinstance(tags, list) else str(tags)

        try:
            db.session.add(task)
            db.session.commit()
            return jsonify(task.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Erro ao criar task'}), 500

    @staticmethod
    def update_task(task_id):
        task = db.session.get(Task, task_id)
        if not task:
            return jsonify({'error': 'Task não encontrada'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados inválidos'}), 400

        if 'title' in data:
            title = str(data['title']).strip()
            if len(title) < 3:
                return jsonify({'error': 'Título muito curto'}), 400
            if len(title) > 200:
                return jsonify({'error': 'Título muito longo'}), 400
            task.title = title

        if 'description' in data:
            task.description = data['description']

        if 'status' in data:
            if data['status'] not in ['pending', 'in_progress', 'done', 'cancelled']:
                return jsonify({'error': 'Status inválido'}), 400
            task.status = data['status']

        if 'priority' in data:
            p = int(data['priority'])
            if p < 1 or p > 5:
                return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400
            task.priority = p

        if 'user_id' in data:
            if data['user_id']:
                user = db.session.get(User, data['user_id'])
                if not user:
                    return jsonify({'error': 'Usuário não encontrado'}), 404
            task.user_id = data['user_id']

        if 'category_id' in data:
            if data['category_id']:
                cat = db.session.get(Category, data['category_id'])
                if not cat:
                    return jsonify({'error': 'Categoria não encontrada'}), 404
            task.category_id = data['category_id']

        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
                except ValueError:
                    return jsonify({'error': 'Formato de data inválido'}), 400
            else:
                task.due_date = None

        if 'tags' in data:
            task.tags = ','.join(data['tags']) if isinstance(data['tags'], list) else str(data['tags'])

        task.updated_at = datetime.now(timezone.utc)

        try:
            db.session.commit()
            return jsonify(task.to_dict()), 200
        except Exception:
            db.session.rollback()
            return jsonify({'error': 'Erro ao atualizar'}), 500

    @staticmethod
    def delete_task(task_id):
        task = db.session.get(Task, task_id)
        if not task:
            return jsonify({'error': 'Task não encontrada'}), 404

        try:
            db.session.delete(task)
            db.session.commit()
            return jsonify({'message': 'Task deletada com sucesso'}), 200
        except Exception:
            db.session.rollback()
            return jsonify({'error': 'Erro ao deletar'}), 500

    @staticmethod
    def search_tasks():
        query = request.args.get('q', '')
        status = request.args.get('status', '')
        priority = request.args.get('priority', '')
        user_id = request.args.get('user_id', '')

        tasks = Task.query

        if query:
            tasks = tasks.filter(
                db.or_(
                    Task.title.like(f'%{query}%'),
                    Task.description.like(f'%{query}%')
                )
            )

        if status:
            tasks = tasks.filter(Task.status == status)

        if priority:
            tasks = tasks.filter(Task.priority == int(priority))

        if user_id:
            tasks = tasks.filter(Task.user_id == int(user_id))

        results = tasks.all()
        return jsonify([t.to_dict() for t in results]), 200

    @staticmethod
    def task_stats():
        total = Task.query.count()
        pending = Task.query.filter_by(status='pending').count()
        in_progress = Task.query.filter_by(status='in_progress').count()
        done = Task.query.filter_by(status='done').count()
        cancelled = Task.query.filter_by(status='cancelled').count()

        all_tasks = Task.query.all()
        now = datetime.now()
        overdue_count = 0
        for t in all_tasks:
            if t.due_date:
                due = t.due_date.replace(tzinfo=None) if t.due_date.tzinfo else t.due_date
                if due < now and t.status not in ('done', 'cancelled'):
                    overdue_count += 1

        stats = {
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
            'overdue': overdue_count,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
        }
        return jsonify(stats), 200
