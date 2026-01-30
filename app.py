from flask import Flask, render_template, request, jsonify, Response
from model_utils import ChurnPredictor
import pandas as pd
from models import db, Customer, Prediction, Upload
import uuid
from datetime import datetime

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///churn_predictions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Initialize predictor
predictor = ChurnPredictor()

@app.route('/')
def index():
    """Home page"""
    return render_template('home.html')
@app.route('/dashboard')
def dashboard():
    """Dashboard page with prediction form"""
    return render_template('dashboard.html')

@app.route('/analytics')
def analytics():
    """Analytics page"""
    return render_template('analytics.html')

@app.route('/batch')
def batch():
    """Batch prediction page"""
    return render_template('batch.html')

@app.route('/history')
def history():
    """View prediction history"""
    return render_template('history.html')

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint for single prediction"""
    try:
        data = request.get_json()
        
        # Make prediction
        prediction, probability = predictor.predict(data)
        
        # Determine risk level
        risk_level = 'High' if probability > 0.7 else ('Medium' if probability > 0.3 else 'Low')
        
        return jsonify({
            'prediction': int(prediction),
            'probability': float(probability),
            'risk_level': risk_level
        })
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/batch-predict', methods=['POST'])
def batch_predict():
    """API endpoint for batch predictions with database storage"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Generate unique upload ID
        upload_id = str(uuid.uuid4())[:8]
        
        # Read CSV
        df = pd.read_csv(file)
        
        # Make predictions
        predictions = []
        probabilities = []
        customers_data = []
        
        for idx, row in df.iterrows():
            customer_data = {
                'Gender': row.get('Gender', 'Male'),
                'SeniorCitizen': int(row.get('SeniorCitizen', 0)),
                'Partner': row.get('Partner', 'No'),
                'Dependents': row.get('Dependents', 'No'),
                'tenure': int(row.get('tenure', 0)),
                'Contract': row.get('Contract', 'Month-to-month'),
                'PaymentMethod': row.get('PaymentMethod', 'Electronic check'),
                'MonthlyCharges': float(row.get('MonthlyCharges', 0)),
                'TotalCharges': float(row.get('TotalCharges', 0)),
                'InternetService': row.get('InternetService', 'No')
            }
            
            pred, prob = predictor.predict(customer_data)
            predictions.append(pred)
            probabilities.append(prob * 100)
            customers_data.append(customer_data)
        
        df['Prediction'] = predictions
        df['Probability'] = probabilities
        df['RiskLevel'] = df['Probability'].apply(
            lambda x: 'High' if x > 70 else ('Medium' if x > 30 else 'Low')
        )
        
        # Save to database
        high_risk = len(df[df['RiskLevel'] == 'High'])
        medium_risk = len(df[df['RiskLevel'] == 'Medium'])
        low_risk = len(df[df['RiskLevel'] == 'Low'])
        
        # Create upload record
        upload = Upload(
            upload_id=upload_id,
            filename=file.filename,
            total_customers=len(df),
            high_risk_count=high_risk,
            medium_risk_count=medium_risk,
            low_risk_count=low_risk
        )
        db.session.add(upload)
        
        # Save customers and predictions
        for idx, row in df.iterrows():
            customer = Customer(
                upload_id=upload_id,
                gender=customers_data[idx]['Gender'],
                senior_citizen=customers_data[idx]['SeniorCitizen'],
                partner=customers_data[idx]['Partner'],
                dependents=customers_data[idx]['Dependents'],
                tenure=customers_data[idx]['tenure'],
                contract=customers_data[idx]['Contract'],
                payment_method=customers_data[idx]['PaymentMethod'],
                monthly_charges=customers_data[idx]['MonthlyCharges'],
                total_charges=customers_data[idx]['TotalCharges'],
                internet_service=customers_data[idx]['InternetService']
            )
            db.session.add(customer)
            db.session.flush()  # Get customer ID
            
            prediction_obj = Prediction(
                customer_id=customer.id,
                will_churn=int(row['Prediction']),
                churn_probability=float(row['Probability']),
                risk_level=row['RiskLevel']
            )
            db.session.add(prediction_obj)
        
        db.session.commit()
        
        # Summary statistics
        total = len(df)
        
        return jsonify({
            'upload_id': upload_id,
            'summary': {
                'total': total,
                'high_risk': high_risk,
                'high_risk_pct': round(high_risk / total * 100, 1),
                'medium_risk': medium_risk,
                'medium_risk_pct': round(medium_risk / total * 100, 1),
                'low_risk': low_risk,
                'low_risk_pct': round(low_risk / total * 100, 1)
            },
            'results': df.to_dict('records')
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in batch prediction: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/download-sample')
def download_sample():
    """Download sample CSV template"""
    sample_data = """Gender,SeniorCitizen,Partner,Dependents,tenure,Contract,PaymentMethod,MonthlyCharges,TotalCharges,InternetService
Male,0,Yes,No,24,One year,Electronic check,65.5,1573.2,DSL
Female,1,No,No,2,Month-to-month,Bank transfer,89.0,178.0,Fiber optic
Male,0,Yes,Yes,48,Two year,Credit card (automatic),70.0,3360.0,DSL
Female,0,No,No,12,Month-to-month,Electronic check,85.5,1026.0,Fiber optic"""
    
    return Response(
        sample_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=sample_customers.csv"}
    )

@app.route('/api/uploads')
def get_uploads():
    """Get all uploads"""
    try:
        uploads = Upload.query.order_by(Upload.created_at.desc()).all()
        return jsonify({
            'uploads': [upload.to_dict() for upload in uploads]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload/<upload_id>')
def get_upload_details(upload_id):
    """Get details of a specific upload"""
    try:
        customers = Customer.query.filter_by(upload_id=upload_id).all()
        results = []
        
        for customer in customers:
            customer_dict = customer.to_dict()
            if customer.prediction:
                customer_dict['prediction'] = customer.prediction.to_dict()
            results.append(customer_dict)
        
        return jsonify({
            'customers': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete-upload/<upload_id>', methods=['DELETE'])
def delete_upload(upload_id):
    """Delete an upload and all its data"""
    try:
        # Delete customers (will cascade to predictions)
        Customer.query.filter_by(upload_id=upload_id).delete()
        
        # Delete upload record
        Upload.query.filter_by(upload_id=upload_id).delete()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Upload deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    try:
        total_customers = Customer.query.count()
        total_uploads = Upload.query.count()
        
        high_risk = Prediction.query.filter_by(risk_level='High').count()
        medium_risk = Prediction.query.filter_by(risk_level='Medium').count()
        low_risk = Prediction.query.filter_by(risk_level='Low').count()
        
        return jsonify({
            'total_customers': total_customers,
            'total_uploads': total_uploads,
            'high_risk': high_risk,
            'medium_risk': medium_risk,
            'low_risk': low_risk
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)