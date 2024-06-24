from flask import Flask, jsonify, request, render_template
from readEmail import read_email_data
from openaiRAG import generate_content_from_documents
import os
from dotenv import load_dotenv

load_dotenv()
host = os.getenv("host")
app = Flask(__name__)


# Route for the home page
@app.route('/')
def home():
    return render_template("index.html", host=host)


# Route to return a JSON response
@app.route('/api/fetch_email', methods=['GET'])
def get_data():
    submission_id = read_email_data()
    if submission_id:
        return jsonify(submission_id), 200
    else:
        return jsonify({"message": "No email received"}), 400


@app.route('/api/generate_data', methods=['GET'])
def generate_data():
    submission_id = request.args.get("submission_id")
    if not submission_id:
        return jsonify({"message": "Please Provide Submission Id"}), 404
    try:
        response = generate_content_from_documents(submission_id=submission_id)
        if not response:
            return jsonify({"message": "No Data Found From the files"}), 200
        return response, 200
    except Exception as e:
        return jsonify({"message": f"Unable to generate response: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
