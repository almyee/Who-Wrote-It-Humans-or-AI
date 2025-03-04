from flask import Flask, request, jsonify

app = Flask(__name__)
data_store = {}

@app.route('/get/<key>', methods=['GET'])
def get_value(key):
    return jsonify({key: data_store.get(key, "Key not found")})

@app.route('/set', methods=['POST'])
def set_value():
    key = request.json.get("key")
    value = request.json.get("value")
    data_store[key] = value
    return jsonify({"message": "Key stored successfully"})

if __name__ == '__main__':
    app.run(port=5000)

