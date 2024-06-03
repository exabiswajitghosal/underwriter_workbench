import awsgi
from flask import Flask, jsonify, request
from readEmail import read_email_data
from openaiRAG import generate_content_from_documents

app = Flask(__name__)


# Route for the home page
@app.route('/')
def home():
    return jsonify(message="Connection Successful"), 200


# Route to return a JSON response
@app.route('/api/fetch_email', methods=['GET'])
def get_data():
    submission_id = read_email_data()
    if submission_id:
        return jsonify(submission_id), 200
    else:
        return jsonify({"message": "No email received"}), 200


@app.route('/api/generate_data', methods=['GET'])
def generate_data():
    submission_id = request.form.get("submission_id")
    response = generate_content_from_documents(submission_id=submission_id)
    return response, 200


def lambda_handler(event, context):
    return awsgi.response(app, event, context, base64_content_types={"image/png"})


if __name__ == '__main__':
    app.run(debug=True)
