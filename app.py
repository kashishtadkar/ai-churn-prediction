from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <html>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🎉 App is WORKING!</h1>
            <p>Railway deployment successful!</p>
        </body>
    </html>
    """

@app.route('/health')
def health():
    return {'status': 'OK', 'message': 'App is running'}

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)