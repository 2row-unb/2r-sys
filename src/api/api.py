"""
API for viewer polling
"""
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

info = None


@app.route("/angles", methods=['GET'])
def angles_view():
    if info:
        response = Response(
            response=info,
            status=200,
            mimetype='application/json'
        )
    else:
        data = {'error': 'Information unavailable'}
        response = jsonify(data)

    return response


@app.route("/info", methods=['POST'])
def info_view():
    print(request.data)
