from flask import Flask, render_template, request, redirect
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFIACTIONS'] = False
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(160), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now())

class TaskResource(Resource):
    def get(self, id: int):
        task = Task.query.get_or_404(id)
        return {
            "id": task.id,
            "content": task.content,
            "created": task.created.isoformat()
        }
    
    def update(self, id: int):
        task = Task.query.get_or_404(id)
        data = request.json
        if 'content' in data:
            task.content = data['content']
        
        try:
            db.session.commit()
            return {"message": "Task updated successfully"}, 200
        except:
            return {"message": "Error updating task"}, 500
        
    def delete(self, id: int):
        task = Task.query.get_or_404(id)
        
        try:
            db.session.delete(task)
            db.session.commit()
            return {"message": "Task deleted successfully"}, 200
        except:
            return {"message": "Error deleting task"}, 500

class TaskListResource(Resource):
    def get(self):
        tasks = Task.query.order_by(Task.created).all()
        return [
            {
                "id": task.id,
                "content": task.content,
                "created": task.created.isoformat()
            } for task in tasks
        ]

    def post(self):
        data = request.json
        if 'content' not in data or not data['content']:
            return {"message": "Content is required"}, 400
        
        new_task = Task(content=data['content'])
        try:
            db.session.add(new_task)
            db.session.commit()
            return {
                "message": "Task created successfully",
                "task": {
                    "id": new_task.id,
                    "content": new_task.content,
                    "created": new_task.created
                }
            }, 201
        except: 
            return {'message': "Error creating task"}, 500


api.add_resource(TaskListResource, "/")
api.add_resource(TaskResource, "/<int:id>")


if __name__ == "__main__":
    app.run(debug=True)
