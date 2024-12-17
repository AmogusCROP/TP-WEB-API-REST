from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Bienvenue sur mon API Flask !"})

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, World!"})

@app.route('/api/data')
def data():
    return jsonify({"data": [1, 2, 3, 4]})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
