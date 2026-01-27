from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import pandas as pd
from prediction import ChurnPredictor
import os

app = Flask(__name__)
CORS(app)

predictor = ChurnPredictor()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/batch')
def batch():
    """Batch prediction page"""
    return render_template('batch.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
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
        
        prediction, probability = predictor.predict(customer_data)
        
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

@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    """API endpoint for batch predictions"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Please upload a CSV file'}), 400
        
        # Read CSV
        df = pd.read_csv(file)
        
        # Validate required columns
        required_columns = ['Gender', 'SeniorCitizen', 'Partner', 'Dependents', 'tenure', 
                          'Contract', 'PaymentMethod', 'MonthlyCharges', 'TotalCharges', 'InternetService']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({'error': f'Missing required columns: {", ".join(missing_columns)}'}), 400
        
        # Make predictions
        predictions = []
        probabilities = []
        
        for idx, row in df.iterrows():
            try:
                customer_data = {
                    'Gender': str(row.get('Gender', 'Male')),
                    'SeniorCitizen': int(row.get('SeniorCitizen', 0)),
                    'Partner': str(row.get('Partner', 'No')),
                    'Dependents': str(row.get('Dependents', 'No')),
                    'tenure': int(row.get('tenure', 0)),
                    'Contract': str(row.get('Contract', 'Month-to-month')),
                    'PaymentMethod': str(row.get('PaymentMethod', 'Electronic check')),
                    'MonthlyCharges': float(row.get('MonthlyCharges', 0)),
                    'TotalCharges': float(row.get('TotalCharges', 0)),
                    'InternetService': str(row.get('InternetService', 'No'))
                }
                
                pred, prob = predictor.predict(customer_data)
                predictions.append('Yes' if pred == 1 else 'No')
                probabilities.append(float(prob * 100))
            except Exception as e:
                print(f"Error processing row {idx}: {str(e)}")
                predictions.append('Error')
                probabilities.append(0.0)
        
        # Create results list
        results = []
        for i in range(len(predictions)):
            results.append({
                'prediction': predictions[i],
                'probability': probabilities[i]
            })
        
        # Calculate risk levels
        high_risk = sum(1 for p in probabilities if p > 70)
        medium_risk = sum(1 for p in probabilities if 30 <= p <= 70)
        low_risk = sum(1 for p in probabilities if p < 30)
        total = len(probabilities)
        
        return jsonify({
            'total': total,
            'high_risk': high_risk,
            'high_risk_percent': round(high_risk / total * 100, 1) if total > 0 else 0,
            'medium_risk': medium_risk,
            'medium_risk_percent': round(medium_risk / total * 100, 1) if total > 0 else 0,
            'low_risk': low_risk,
            'low_risk_percent': round(low_risk / total * 100, 1) if total > 0 else 0,
            'results': results
        })
        
    except pd.errors.EmptyDataError:
        return jsonify({'error': 'The uploaded CSV file is empty'}), 400
    except pd.errors.ParserError:
        return jsonify({'error': 'Error parsing CSV file. Please check the file format'}), 400
    except Exception as e:
        print(f"Error in batch prediction: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/download-sample')
def download_sample():
    """Download sample CSV template"""
    sample_data = """Gender,SeniorCitizen,Partner,Dependents,tenure,Contract,PaymentMethod,MonthlyCharges,TotalCharges,InternetService
Male,0,Yes,No,24,One year,Electronic check,65.5,1573.2,DSL
Female,1,No,No,2,Month-to-month,Bank transfer,89.0,178.0,Fiber optic
Male,0,Yes,Yes,48,Two year,Credit card (automatic),70.0,3360.0,DSL
Female,0,No,No,12,Month-to-month,Electronic check,85.5,1026.0,Fiber optic
Male,1,Yes,No,36,One year,Electronic check,95.0,3420.0,Fiber optic"""
    
    return Response(
        sample_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=sample_customers.csv"}
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)