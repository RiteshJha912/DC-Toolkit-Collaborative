from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This allows cross-origin requests from React frontend

@app.route('/process', methods=['POST'])
def process_input():
    data = request.json
    user_input = data.get('input')  # Get the input from React frontend
    output = user_input  # Echo back the input
    return jsonify({'output': output})  # Return it as JSON

if __name__ == '__main__':
    app.run(debug=True)
