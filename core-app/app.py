from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify(status="ok", service="core-app")


if __name__ == "__main__":
    app.run(port=3000, debug=True)
