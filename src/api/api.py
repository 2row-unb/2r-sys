"""
API for viewer polling
"""
from flask import Flask, request, jsonify
import sys

app = Flask(__name__)

info = None


@app.route("/angles", methods=['GET'])
def angles_view():
    global info
    response = info or {'error': 'Information unavailable'}
    return jsonify(response)


@app.route("/info", methods=['POST'])
def info_view():
    global info
    info = request.json
    print(request.json, file=sys.stderr)
    return 'ok'
