from symtable import Class

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

class NoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)

    def repr(self):
        return f'Description: {self.description}, Done: {self.done}'

note_args = reqparse.RequestParser()
note_args.add_argument('title', type=str, required=True, help="title is required")
note_args.add_argument('description', type=str, required=True, help="description is required")
note_args.add_argument('done', type=bool, required=False, help="done can be true or false")

note_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
}

class Notes(Resource):
    @marshal_with(note_fields)
    def get(self):
        notes = NoteModel.query.all()
        return notes

    @marshal_with(note_fields)
    def post(self):
        args = note_args.parse_args()
        note = NoteModel(title=args['title'], description=args['description'], done=args['done'])
        db.session.add(note)
        db.session.commit()
        notes = NoteModel.query.all()
        return notes, 201

class Note(Resource):
    @marshal_with(note_fields)
    def get(self, id):
        note = NoteModel.query.filter_by(id=id).first()
        if not note:
            abort(404, message="Note not found")
        return note

    @marshal_with(note_fields)
    def patch(self, id):
        args = note_args.parse_args()
        note = NoteModel.query.filter_by(id=id).first()
        if not note:
            abort(404, message="Note not found")
        note.title = args['title']
        note.description = args['description']
        note.done = args['done']
        db.session.commit()
        return note

    @marshal_with(note_fields)
    def delete(self, id):
        note = NoteModel.query.filter_by(id=id).first()
        if not note:
            abort(404, message="Note not found")
        db.session.delete(note)
        db.session.commit()
        notes = NoteModel.query.all()
        return notes


api.add_resource(Notes, '/api/notes/')
api.add_resource(Note, '/api/notes/<int:id>')

@app.route('/')
def home ():
    return "Hello World"

if __name__ == '__main__':
    app.run(debug=True)

