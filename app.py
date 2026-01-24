from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
from prediction import ChurnPredictor
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize predictor
predictor = ChurnPredictor()

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form data
        gender = request.form.get('gender')
        senior_citizen = int(request.form.get('senior_citizen', 0))
        partner = request.form.get('partner')
        dependents = request.form.get('dependents')
        tenure = int(request.form.get('tenure', 0))
        contract = request.form.get('contract')
        payment_method = request.form.get('payment_method')
        monthly_charges = float(request.form.get('monthly_charges', 0))
        total_charges = float(request.form.get('total_charges', 0))
        internet_service = request.form.get('internet_service')
        
        # Create customer data dictionary
        customer_data = {
            'Gender': gender,
            'SeniorCitizen': senior_citizen,
            'Partner': partner,
            'Dependents': dependents,
            'tenure': tenure,
            'Contract': contract,
            'PaymentMethod': payment_method,
            'MonthlyCharges': monthly_charges,
            'TotalCharges': total_charges,
            'InternetService': internet_service
        }
        
        # Make prediction using ChurnPredictor
        prediction, probability = predictor.predict(customer_data)
        
        # Return JSON response
        return jsonify({
            'prediction': 'Yes' if prediction == 1 else 'No',
            'churn_probability': float(probability * 100)
        })
        
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Error making prediction',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)