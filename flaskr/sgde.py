from flask import Blueprint, request, abort

from flaskr.db import get_db


bp = Blueprint('sgde', __name__)


@bp.route('/tasks', methods=['GET'])
def get_tasks():
    db = get_db()
    tasks = db.execute('SELECT * FROM task').fetchall()
    results = [dict(row) for row in tasks]
    return results


@bp.route('/tasks/<string:task_id>', methods=['GET'])
def get_task(task_id):
    db = get_db()
    task = db.execute('SELECT * FROM task WHERE id == ?', (task_id,)).fetchone()

    if task is None:
        abort(400, f'Task {task_id} does not exist.')

    return dict(task)


@bp.route('/tasks', methods=['POST'])
def submit_tasks():
    task_name = request.form['task_name']
    description = request.form['description']
    labels = request.form['labels']

    if not task_name:
        abort(400, "Task name not provided.")

    if not description:
        abort(400, "Task description not provided.")

    if not labels:
        abort(400, "Task labels not provided.")

    db = get_db()
    db.execute(
        'INSERT INTO task (task_name, description, labels)'
        ' VALUES (?, ?, ?)',
        (task_name, description, labels)
    )
    db.commit()

    return "Task created."


@bp.route('/tasks/<string:task_id>/generators', methods=['GET'])
def get_generators(task_id):
    db = get_db()
    task = db.execute('SELECT * FROM task WHERE id == ?', (task_id,)).fetchone()

    if task is None:
        abort(400, f'Task {task_id} does not exist.')

    tasks = db.execute('SELECT * FROM generator WHERE task_id == ?', (task_id,)).fetchall()
    results = [dict(row) for row in tasks]
    return results


@bp.route('/tasks/<string:task_id>/generators/<string:gen_id>', methods=['GET'])
def get_generator(task_id, gen_id):
    db = get_db()
    task = db.execute('SELECT * FROM task WHERE id == ?', (task_id,)).fetchone()

    if task is None:
        abort(400, f'Task {task_id} does not exist.')

    generator = db.execute('SELECT * FROM generator WHERE (id, task_id) == (?, ?)', (gen_id, task_id,)).fetchone()

    if generator is None:
        abort(400, f'Generator {gen_id} does not exist.')

    return dict(generator)


@bp.route('/tasks/<string:task_id>/generators', methods=['POST'])
def submit_generator(task_id):
    db = get_db()
    task = db.execute('SELECT * FROM task WHERE id == ?', (task_id,)).fetchone()

    if task is None:
        abort(400, f'Task {task_id} does not exist.')

    task_id = request.form['task_id']
    params = request.form['params']

    if not task_id:
        abort(400, "Generator task not provided.")

    if not params:
        abort(400, "Generator parameters not provided.")

    db = get_db()
    db.execute(
        'INSERT INTO generator (params, task_id)'
        ' VALUES (?, ?)',
        (params, task_id)
    )
    db.commit()

    return "Generator created."
