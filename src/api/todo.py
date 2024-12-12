import hashlib
from flask import Blueprint, request, jsonify, make_response
from datetime import datetime
from src.db.db_connection import byte_master_connection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
import logging

logger = logging.getLogger(__name__)

to_do = Blueprint('todo', __name__)


@to_do.route('/todo', methods=['POST'])
def todo():
    try:
        data = request.get_json()

        if 'tasks' not in data or not isinstance(data['tasks'], list):
            return jsonify({"error": "Missing 'tasks' field or 'tasks' is not a list."}), 400

        tasks = data['tasks']

        for task_data in tasks:
            if 'task' not in task_data or 'due_date' not in task_data:
                return jsonify({"error": "Each task must include 'task' and 'due_date' fields."}), 400

            task = task_data['task']
            due_date_str = task_data['due_date']

            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({"error": f"Invalid date format for task '{task}'. Use YYYY-MM-DD."}), 400

            task_hash = hashlib.sha256(task.encode()).hexdigest()

            query = text("""
                INSERT INTO todo_tasks (task, due_date, task_hash) 
                VALUES (:task, :due_date, :task_hash)
            """)

            with byte_master_connection() as session:
                session.execute(query, {'task': task, 'due_date': due_date, 'task_hash': task_hash})
                session.commit()

        return jsonify({"message": f"{len(tasks)} task(s) added successfully"}), 200

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@to_do.route('/get_todo_list', methods=['GET'])
def get_todo():
    try:
        with byte_master_connection() as session:
            query = text(""" SELECT id, task, due_date FROM todo_tasks ORDER BY id ASC """)
            results = session.execute(query).fetchall()
            data = []
            for res in results:
                data.append({
                    "id": res[0],
                    "task": res[1],
                    "due_date": res[2]
                })
            logger.info(f"Successfully retrieved data from todo_tasks")
            return make_response(jsonify(data), 200)

    except Exception as e:

        logger.error(f"Error fetching bg_index_package_mapping data: {str(e)}")

        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve data from todo_tasks.'
        }), 500


@to_do.route('/clear_todo/<int:id>', methods=['DELETE'])
def clear_todo(id):
    transaction = None
    try:
        with byte_master_connection() as session:
            transaction = session.begin()
            query = text("""DELETE FROM todo_tasks
                            WHERE id=:id""")
            results = session.execute(query, {"id": id})
            if results.rowcount == 0:
                transaction.rollback()
                logger.error(f"Task with id {id} is not found")
                return make_response(jsonify({"message": "Task not found"}), 404)

            transaction.commit()
            logger.info(f"Task with id {id} deleted successfully")
            return make_response(jsonify({"message": "Task Deleted Successfully"}), 200)
    except Exception as e:
        if transaction is not None:
            transaction.rollback()
        logger.error(f"Error deleting task with id {id}: {str(e)}")
        return make_response(jsonify({"message": "Failed to delete the record."}), 500)
