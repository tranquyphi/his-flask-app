from flask import Flask

# Create Flask application instance
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World! Flask app is running successfully!"

@app.route('/health')
def health():
    return {"status": "healthy", "message": "Service is running"}

@app.route('/test')
def test():
    return {"message": "Test endpoint works!", "app": "his.py Flask application"}

if __name__ == '__main__':
    # For development only
    app.run(host='0.0.0.0', port=5000, debug=True)