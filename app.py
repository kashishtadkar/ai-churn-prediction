from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
from prediction import ChurnPredictor
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize predictor
print("🚀 Initializing Churn Predictor...")
predictor = ChurnPredictor()
print("✅ Server ready!")

@app.route('/')
def home():
    """Serve the dashboard"""
    return render_template('dashboard.html')

@app.route('/api/predict', methods=['POST'])
def predict_single():
    """
    API endpoint for single customer prediction
    
    Request body example:
    {
        "gender": "Male",
        "tenure": 3,
        "MonthlyCharges": 95.0,
        ...
    }
    """
    try:
        customer_data = request.json
        result = predictor.predict(customer_data)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/predict/batch', methods=['POST'])
def predict_batch():
    """
    API endpoint for batch prediction
    
    Request body example:
    {
        "customers": [
            {...customer1...},
            {...customer2...}
        ]
    }
    """
    try:
        customers = request.json.get('customers', [])
        results = predictor.predict_batch(customers)
        return jsonify({
            'success': True,
            'count': len(results),
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    # These would come from a database in production
    stats = {
        'model_accuracy': 95.56,
        'precision_score': 93.01,
        'predictions_today': 2489,
        'revenue_saved': 2400000,
        'total_customers': 9500,
        'high_risk_customers': 876,
        'churn_rate': 12.5
    }
    return jsonify(stats)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Churn Prediction API is running'
    })

if __name__ == '__main__':
    import os
    
    # Get port from environment variable (Render provides this)
    # If not found, use 5000 (for local development)
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "="*60)
    print("🎯 CHURN PREDICTION API SERVER")
    print("="*60)
    print(f"📡 Server running on port: {port}")
    print("="*60 + "\n")
    
    # debug=False for production (security)
    # host='0.0.0.0' means accept connections from anywhere
    app.run(debug=False, host='0.0.0.0', port=port)