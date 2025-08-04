from flask import Flask, jsonify
from netlify_functions_wsgi import handle_request

app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Test function working!", "status": "success"})

def handler(event, context):
    return handle_request(app, event, context) 