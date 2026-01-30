from flask import Flask, render_template, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import uuid
import os

# Initialize Flask app
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///churn_predictions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Initialize database
db = SQLAlchemy()
db.init_app(app)

# Import model_utils
try:
    from model_utils import ChurnPredictor
    predictor = ChurnPredictor()
    print("✅ ChurnPredictor loaded successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not load ChurnPredictor: {e}")
    predictor = None

# Define models inline
class Upload(db.Model):
    _tablename_ = 'uploads'
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.String(50), unique=True, nullable=False)
    filename = db.Column(db.String(255))
    total_customers = db.Column(db.Integer)
    high_risk_count = db.Column(db.Integer)
    medium_risk_count = db.Column(db.Integer)
    low_risk_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'upload_id': self.upload_id,
            'filename': self.filename,
            'total_customers': self.total_customers,
            'high_risk_count': self.high_risk_count,
            'medium_risk_count': self.medium_risk_count,
            'low_risk_count': self.low_risk_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Customer(db.Model):
    _tablename_ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10))
    senior_citizen = db.Column(db.Integer)
    partner = db.Column(db.String(10))
    dependents = db.Column(db.String(10))
    tenure = db.Column(db.Integer)
    contract = db.Column(db.String(50))
    payment_method = db.Column(db.String(50))
    monthly_charges = db.Column(db.Float)
    total_charges = db.Column(db.Float)
    internet_service = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'upload_id': self.upload_id,
            'gender': self.gender,
            'senior_citizen': self.senior_citizen,
            'partner': self.partner,
            'dependents': self.dependents,
            'tenure': self.tenure,
            'contract': self.contract,
            'payment_method': self.payment_method,
            'monthly_charges': self.monthly_charges,
            'total_charges': self.total_charges,
            'internet_service': self.internet_service,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Prediction(db.Model):
    _tablename_ = 'predictions'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    will_churn = db.Column(db.Integer)
    churn_probability = db.Column(db.Float)
    risk_level = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    customer = db.relationship('Customer', backref=db.backref('prediction', uselist=False, cascade='all, delete-orphan'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'will_churn': self.will_churn,
            'churn_probability': self.churn_probability,
            'risk_level': self.risk_level,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# Initialize database
def init_db():
    try:
        with app.app_context():
            db.create_all()
            print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")

init_db()

# Routes
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/batch')
def batch():
    return render_template('batch.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/health')
def health():
    return 'OK', 200

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if predictor:
            prediction, probability = predictor.predict(data)
            risk_level = 'High' if probability > 0.7 else ('Medium' if probability > 0.3 else 'Low')
            return jsonify({
                'prediction': int(prediction),
                'probability': float(probability),
                'risk_level': risk_level
            })
        else:
            return jsonify({'error': 'Predictor not available'}), 500
    except Exception as e:
        print(f"Error in prediction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/batch-predict', methods=['POST'])
def batch_predict():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        upload_id = str(uuid.uuid4())[:8]
        df = pd.read_csv(file)
        
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
            
            if predictor:
                pred, prob = predictor.predict(customer_data)
            else:
                pred, prob = 0, 0.5
            
            predictions.append(pred)
            probabilities.append(prob * 100)
            customers_data.append(customer_data)
        
        df['Prediction'] = predictions
        df['Probability'] = probabilities
        df['RiskLevel'] = df['Probability'].apply(
            lambda x: 'High' if x > 70 else ('Medium' if x > 30 else 'Low')
        )
        
        # Save to database
        try:
            high_risk = len(df[df['RiskLevel'] == 'High'])
            medium_risk = len(df[df['RiskLevel'] == 'Medium'])
            low_risk = len(df[df['RiskLevel'] == 'Low'])
            
            upload = Upload(
                upload_id=upload_id,
                filename=file.filename,
                total_customers=len(df),
                high_risk_count=high_risk,
                medium_risk_count=medium_risk,
                low_risk_count=low_risk
            )
            db.session.add(upload)
            
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
                db.session.flush()
                
                prediction_obj = Prediction(
                    customer_id=customer.id,
                    will_churn=int(row['Prediction']),
                    churn_probability=float(row['Probability']),
                    risk_level=row['RiskLevel']
                )
                db.session.add(prediction_obj)
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Database save error: {e}")
        
        total = len(df)
        high_risk = len(df[df['RiskLevel'] == 'High'])
        medium_risk = len(df[df['RiskLevel'] == 'Medium'])
        low_risk = len(df[df['RiskLevel'] == 'Low'])
        
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
        print(f"Error in batch prediction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/download-sample')
def download_sample():
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
    try:
        uploads = Upload.query.order_by(Upload.created_at.desc()).all()
        return jsonify({'uploads': [upload.to_dict() for upload in uploads]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload/<upload_id>')
def get_upload_details(upload_id):
    try:
        customers = Customer.query.filter_by(upload_id=upload_id).all()
        results = []
        for customer in customers:
            customer_dict = customer.to_dict()
            if customer.prediction:
                customer_dict['prediction'] = customer.prediction.to_dict()
            results.append(customer_dict)
        return jsonify({'customers': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete-upload/<upload_id>', methods=['DELETE'])
def delete_upload(upload_id):
    try:
        Customer.query.filter_by(upload_id=upload_id).delete()
        Upload.query.filter_by(upload_id=upload_id).delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Upload deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)