from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)

TASKS = {
    'task1': {'task': 'build an API'},
    'task2': {'task': '?????'},
    'task3': {'task': 'profit!'},
}


def abort_if_todo_doesnt_exist(task_id):
    if task_id not in TASKS:
        abort(404, message="Task {} doesn't exist".format(task_id))


parser = reqparse.RequestParser()
parser.add_argument('task')


# Task
# shows a single task item and lets you delete a task item
class Task(Resource):
    def get(self, task_id):
        abort_if_todo_doesnt_exist(task_id)
        return TASKS[task_id]

    def delete(self, task_id):
        abort_if_todo_doesnt_exist(task_id)
        del TASKS[task_id]
        return '', 204

    def put(self, task_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        TASKS[task_id] = task
        return task, 201


# TaskList
# shows a list of all tasks, and lets you POST to add new tasks
class TaskList(Resource):
    def get(self):
        return TASKS

    def post(self):
        args = parser.parse_args()
        task_id = int(max(TASKS.keys()).lstrip('task')) + 1
        task_id = 'task{}'.format(task_id)
        TASKS[task_id] = {'task': args['task']}
        return TASKS[task_id], 201


# Actually setup the Api resource routing here

api.add_resource(TaskList, '/tasks')
api.add_resource(Task, '/tasks/<task_id>')

if __name__ == '__main__':
    app.run(debug=True)
