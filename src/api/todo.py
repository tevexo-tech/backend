from flask import request, jsonify, make_response
from flask_restful import Resource
from datetime import datetime
from sqlalchemy.sql import text
from src.db.db_connection import byte_master_connection
import logging
import hashlib

from src.utils.utils import token_required
from src.utils.user_details import UserDetails, AuthError
import jwt

logger = logging.getLogger(__name__)

class Todo(Resource):
    method_decorators = [token_required]

    def post(self):
        try:
            user = UserDetails.get_current_user()   # returns dict or raises
            candidate_id = str(user["candidate_id"])

            data = request.get_json() or {}
            if 'tasks' not in data or not isinstance(data['tasks'], list):
                return {"error": "Missing 'tasks' field or 'tasks' is not a list."}, 400

            tasks = data['tasks']
            with byte_master_connection() as session:
                for task_data in tasks:
                    # ... same validation and insert as before ...
                    pass
            return {"message": f"{len(tasks)} task(s) added for {candidate_id}"}, 200

        except AuthError as ae:
            return {"error": str(ae)}, ae.code
        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}, 401
        except Exception as e:
            logger.exception("POST /todo error")
            return {"error": "Internal server error"}, 500

    def get(self):
        try:
            user = UserDetails.get_current_user()
            candidate_id = str(user["candidate_id"])

            with byte_master_connection() as session:
                query = text("""
                    SELECT id, task, due_date
                    FROM todo_tasks
                    WHERE candidate_id = :candidate_id
                    ORDER BY id ASC
                """)
                results = session.execute(query, {"candidate_id": candidate_id}).fetchall()

                data = [
                    {"id": r[0], "task": r[1], "due_date": str(r[2])}
                    for r in results
                ]
            return make_response(jsonify(data), 200)

        except AuthError as ae:
            return {"error": str(ae)}, ae.code
        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}, 401
        except Exception as e:
            logger.exception("GET /todo error")
            return {"error": "Internal server error"}, 500

    def delete(self, id):
        try:
            user = UserDetails.get_current_user()
            candidate_id = str(user["candidate_id"])

            with byte_master_connection() as session:
                transaction = session.begin()

                # only delete if the task belongs to the same candidate
                query = text("""
                        DELETE FROM todo_tasks
                        WHERE id = :id AND candidate_id = :candidate_id
                    """)
                results = session.execute(query, {"id": id, "candidate_id": candidate_id})

                if results.rowcount == 0:
                    transaction.rollback()
                    return {"message": "Task not found or not authorized"}, 404

                transaction.commit()
                return {"message": "Task deleted successfully"}, 200

        except Exception as e:
            if transaction:
                transaction.rollback()
            logger.exception(f"Error deleting task {id}")
            return {"message": "Failed to delete the record."}, 500