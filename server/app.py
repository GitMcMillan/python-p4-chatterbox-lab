from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)


@app.route('/messages', methods=["GET", "POST"])
def messages():
    if request.method == "GET":
        # Return array of all messages as JSON
        messages = []
        for message in Message.query.order_by(Message.created_at.asc()).all():
            # Build the dict body
            message_dict = {
                "id": message.id,
                "body": message.body,
                "username": message.username,
                "created_at": message.created_at,
                "updated_at": message.updated_at
            }
            messages.append(message_dict)
        
        # Return the response
        response = make_response(
            jsonify(messages),
            200
        )
        return response
    
    elif request.method == "POST":
        # Create a new message using JSON input
        body = request.json.get("body")
        username = request.json.get("username")
        created_at = request.json.get("created_at")
        updated_at = request.json.get("updated_at")

        # Validate that required fields are present
        if not body or not username:
            return make_response(
                jsonify({"error": "Both 'body' and 'username' are required."}),
                400  # Bad Request if body or username is missing
            )

        # Create the new message
        new_message = Message(
            body=body,
            username=username,
            created_at=created_at,
            updated_at=updated_at
        )

        db.session.add(new_message)
        db.session.commit()

        message_dict = new_message.to_dict()

        response = make_response(
            jsonify(message_dict),
            201  # Created
        )
        return response


@app.route('/messages/<int:id>', methods=["PATCH", "DELETE"])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()

    if not message:
        return make_response(
            jsonify({"Error": "Message not found"}),
            404
        )

    if request.method == 'PATCH':
        # Use JSON input instead of form data
        body = request.json.get("body")

        if not body:
            return make_response(
                jsonify({"error": "The 'body' parameter is required to update the message."}),
                400  # Bad Request if body is not provided
            )

        # Update message body
        message.body = body
        db.session.commit()

        message_dict = message.to_dict()

        response = make_response(
            jsonify(message_dict),
            200
        )
        return response

    elif request.method == 'DELETE':
        # Delete the message from the database
        db.session.delete(message)
        db.session.commit()

        response_body = {
            "delete_successful": True,
            "message": "Message deleted."
        }

        response = make_response(
            jsonify(response_body),
            200
        )
        return response


if __name__ == '__main__':
    app.run(port=5555)