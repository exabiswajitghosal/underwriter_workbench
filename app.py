from flask import Flask, jsonify, request, render_template
from readEmail import read_email_data
from openaiRAG import generate_content_from_documents

app = Flask(__name__)


# Route for the home page
@app.route('/')
def home():
    return render_template("index.html")


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
    submission_id = read_email_data()
    if not submission_id:
        return render_template('index.html', message="No Email Received.")
    try:
        response = generate_content_from_documents(submission_id=submission_id)
        if not response:
            return render_template('index.html', message="No Files found")
        return render_template('index.html', response=response, message="Files extracted successfully")
    except:
        return render_template('index.html',message="Unable to generate response")


if __name__ == '__main__':
    app.run(debug=True)
