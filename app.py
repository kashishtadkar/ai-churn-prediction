from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Churn Prediction</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { 
                margin: 0; 
                padding: 0; 
                box-sizing: border-box; 
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            
            nav {
                background: rgba(255, 255, 255, 0.95);
                padding: 1rem 2rem;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                position: sticky;
                top: 0;
                z-index: 1000;
            }
            
            nav ul {
                list-style: none;
                display: flex;
                gap: 2rem;
                justify-content: center;
                flex-wrap: wrap;
            }
            
            nav a {
                text-decoration: none;
                color: #333;
                font-weight: 600;
                transition: color 0.3s;
                font-size: 1.1rem;
            }
            
            nav a:hover { 
                color: #667eea; 
            }
            
            .container {
                text-align: center;
                color: white;
                padding: 100px 20px;
                animation: fadeIn 1s ease-out;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            h1 { 
                font-size: 3.5rem; 
                margin-bottom: 1rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            
            .subtitle {
                font-size: 1.5rem; 
                margin-bottom: 30px;
                opacity: 0.95;
            }
            
            .btn {
                display: inline-block;
                padding: 18px 40px;
                background: white;
                color: #667eea;
                text-decoration: none;
                border-radius: 12px;
                font-weight: 700;
                font-size: 1.2rem;
                margin-top: 20px;
                transition: all 0.3s;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            .btn:hover { 
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            }
            
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 30px;
                max-width: 1200px;
                margin: 60px auto;
                padding: 0 20px;
            }
            
            .feature-card {
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(10px);
                padding: 30px;
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                transition: transform 0.3s;
            }
            
            .feature-card:hover {
                transform: translateY(-10px);
            }
            
            .feature-icon {
                font-size: 3rem;
                margin-bottom: 15px;
            }
            
            .feature-title {
                font-size: 1.3rem;
                font-weight: 700;
                margin-bottom: 10px;
            }
            
            @media (max-width: 768px) {
                h1 { font-size: 2.5rem; }
                .subtitle { font-size: 1.2rem; }
                nav ul { gap: 1rem; }
            }
        </style>
    </head>
    <body>
        <nav>
            <ul>
                <li><a href="/">🏠 Home</a></li>
                <li><a href="/dashboard">📊 Dashboard</a></li>
                <li><a href="/batch">📤 Batch</a></li>
                <li><a href="/history">📜 History</a></li>
                <li><a href="/analytics">📈 Analytics</a></li>
            </ul>
        </nav>
        
        <div class="container">
            <h1>🤖 AI Churn Prediction</h1>
            <p class="subtitle">Predict customer churn with machine learning!</p>
            <a href="/dashboard" class="btn">Try Demo Now →</a>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Single Predictions</div>
                <p>Predict churn for individual customers</p>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">📤</div>
                <div class="feature-title">Batch Upload</div>
                <p>Process thousands of customers at once</p>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">📜</div>
                <div class="feature-title">History Tracking</div>
                <p>View all past predictions</p>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">📈</div>
                <div class="feature-title">Analytics</div>
                <p>Visualize trends and insights</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/dashboard')
def dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - AI Churn Prediction</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .nav-bar {
                background: white;
                padding: 15px 30px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .nav-bar a {
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
                font-size: 1.1rem;
            }
            .content {
                background: white;
                padding: 50px;
                border-radius: 20px;
                max-width: 800px;
                margin: 0 auto;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            h1 { 
                color: #333; 
                margin-bottom: 20px;
                font-size: 2.5rem;
            }
            p { 
                color: #666; 
                font-size: 1.2rem;
                line-height: 1.6;
            }
            .status {
                background: #e7f3ff;
                padding: 20px;
                border-radius: 10px;
                margin-top: 30px;
                border-left: 4px solid #667eea;
            }
        </style>
    </head>
    <body>
        <div class="nav-bar">
            <a href="/">← Back to Home</a>
        </div>
        
        <div class="content">
            <h1>📊 Dashboard Page</h1>
            <p>This is where the prediction dashboard will be!</p>
            
            <div class="status">
                <h3>✅ Navigation Working!</h3>
                <p>You can now navigate between all pages.</p>
                <p style="margin-top: 15px; font-size: 0.9rem;">
                    Next step: Deploy full app with all features!
                </p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/batch')
def batch():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Batch Upload - AI Churn Prediction</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .nav-bar {
                background: white;
                padding: 15px 30px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .nav-bar a {
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
                font-size: 1.1rem;
            }
            .content {
                background: white;
                padding: 50px;
                border-radius: 20px;
                max-width: 800px;
                margin: 0 auto;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            h1 { 
                color: #333; 
                margin-bottom: 20px;
                font-size: 2.5rem;
            }
            .upload-icon {
                font-size: 5rem;
                margin: 30px 0;
            }
        </style>
    </head>
    <body>
        <div class="nav-bar">
            <a href="/">← Back to Home</a>
        </div>
        
        <div class="content">
            <h1>📤 Batch Upload Page</h1>
            <div class="upload-icon">📁</div>
            <p style="color: #666; font-size: 1.2rem;">CSV batch upload feature coming soon!</p>
            <p style="color: #999; margin-top: 20px;">Deploy the full app to upload CSV files.</p>
        </div>
    </body>
    </html>
    """

@app.route('/history')
def history():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>History - AI Churn Prediction</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .nav-bar {
                background: white;
                padding: 15px 30px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .nav-bar a {
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
                font-size: 1.1rem;
            }
            .content {
                background: white;
                padding: 50px;
                border-radius: 20px;
                max-width: 800px;
                margin: 0 auto;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            h1 { 
                color: #333; 
                margin-bottom: 20px;
                font-size: 2.5rem;
            }
        </style>
    </head>
    <body>
        <div class="nav-bar">
            <a href="/">← Back to Home</a>
        </div>
        
        <div class="content">
            <h1>📜 History Page</h1>
            <p style="color: #666; font-size: 1.2rem; margin-top: 20px;">
                Prediction history will appear here!
            </p>
            <p style="color: #999; margin-top: 20px;">
                Database integration coming with full app.
            </p>
        </div>
    </body>
    </html>
    """

@app.route('/analytics')
def analytics():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Analytics - AI Churn Prediction</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .nav-bar {
                background: white;
                padding: 15px 30px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .nav-bar a {
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
                font-size: 1.1rem;
            }
            .content {
                background: white;
                padding: 50px;
                border-radius: 20px;
                max-width: 800px;
                margin: 0 auto;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            h1 { 
                color: #333; 
                margin-bottom: 20px;
                font-size: 2.5rem;
            }
            .chart-placeholder {
                font-size: 4rem;
                margin: 30px 0;
            }
        </style>
    </head>
    <body>
        <div class="nav-bar">
            <a href="/">← Back to Home</a>
        </div>
        
        <div class="content">
            <h1>📈 Analytics Page</h1>
            <div class="chart-placeholder">📊</div>
            <p style="color: #666; font-size: 1.2rem;">
                Charts and analytics dashboard coming soon!
            </p>
            <p style="color: #999; margin-top: 20px;">
                Deploy full app with database to see visualizations.
            </p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {'status': 'OK', 'message': 'App is running with navigation!'}

if __name__ == '_main_':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)