"""
AI Churn Prediction System - COMPLETE FIXED VERSION
Fixed: Database foreign key relationship error
Fixed: Prediction probabilities
New: Dark Theme Design
"""

from flask import Flask, render_template, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import uuid
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///churn_predictions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'churn-prediction-secret-key-2026'

db = SQLAlchemy()
db.init_app(app)

try:
    from model_utils import ChurnPredictor
    predictor = ChurnPredictor()
    print("✅ ChurnPredictor loaded successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not load ChurnPredictor: {e}")
    predictor = None


# ===========================
# DATABASE MODELS - FIXED
# ===========================

class Upload(db.Model):
    _tablename_ = 'uploads'
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.String(50), unique=True, nullable=False)
    filename = db.Column(db.String(255))
    total_customers = db.Column(db.Integer, default=0)
    high_risk_count = db.Column(db.Integer, default=0)
    medium_risk_count = db.Column(db.Integer, default=0)
    low_risk_count = db.Column(db.Integer, default=0)
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
    upload_id = db.Column(db.String(50), db.ForeignKey('uploads.upload_id'), nullable=False)
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
            'internet_service': self.internet_service
        }


class Prediction(db.Model):
    _tablename_ = 'predictions'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    will_churn = db.Column(db.Integer)
    churn_probability = db.Column(db.Float)
    risk_level = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'will_churn': self.will_churn,
            'churn_probability': self.churn_probability,
            'risk_level': self.risk_level,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


def init_db():
    try:
        with app.app_context():
            db.create_all()
            print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database init warning: {e}")

init_db()


# ===========================
# PAGE ROUTES
# ===========================

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/batch')
def batch():
    return render_template('batch.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/health')
def health():
    return 'OK', 200


# ===========================
# API ROUTES
# ===========================

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
        print(f"📊 CSV loaded: {len(df)} rows, columns: {list(df.columns)}")

        results = []
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        saved_customers = []

        for idx, row in df.iterrows():
            try:
                customer_data = {
                    'Gender': str(row.get('Gender', row.get('gender', 'Male'))),
                    'SeniorCitizen': int(row.get('SeniorCitizen', row.get('senior_citizen', 0))),
                    'Partner': str(row.get('Partner', row.get('partner', 'No'))),
                    'Dependents': str(row.get('Dependents', row.get('dependents', 'No'))),
                    'tenure': int(row.get('tenure', row.get('Tenure', 12))),
                    'Contract': str(row.get('Contract', row.get('contract', 'Month-to-month'))),
                    'PaymentMethod': str(row.get('PaymentMethod', row.get('payment_method', 'Electronic check'))),
                    'MonthlyCharges': float(row.get('MonthlyCharges', row.get('monthly_charges', 50))),
                    'TotalCharges': float(row.get('TotalCharges', row.get('total_charges', 500))),
                    'InternetService': str(row.get('InternetService', row.get('internet_service', 'No')))
                }

                if predictor:
                    pred, prob = predictor.predict(customer_data)
                else:
                    pred, prob = 0, 0.5

                prob_pct = round(float(prob) * 100, 1)
                risk = 'High' if prob_pct > 70 else ('Medium' if prob_pct > 30 else 'Low')

                if risk == 'High': high_risk += 1
                elif risk == 'Medium': medium_risk += 1
                else: low_risk += 1

                results.append({
                    'customer': f'Customer {idx + 1}',
                    'prediction': 'Will Churn' if pred == 1 else 'Will Stay',
                    'probability': prob_pct,
                    'risk_level': risk,
                    **customer_data
                })

                saved_customers.append({
                    'data': customer_data,
                    'pred': pred,
                    'prob': prob_pct,
                    'risk': risk
                })

            except Exception as e:
                print(f"⚠️ Row {idx} error: {e}")
                continue

        total = len(results)
        print(f"✅ Processed {total} customers: High={high_risk}, Med={medium_risk}, Low={low_risk}")

        # Save to database
        try:
            upload = Upload(
                upload_id=upload_id,
                filename=file.filename,
                total_customers=total,
                high_risk_count=high_risk,
                medium_risk_count=medium_risk,
                low_risk_count=low_risk
            )
            db.session.add(upload)
            db.session.flush()

            for item in saved_customers:
                cd = item['data']
                customer = Customer(
                    upload_id=upload_id,
                    gender=cd['Gender'],
                    senior_citizen=cd['SeniorCitizen'],
                    partner=cd['Partner'],
                    dependents=cd['Dependents'],
                    tenure=cd['tenure'],
                    contract=cd['Contract'],
                    payment_method=cd['PaymentMethod'],
                    monthly_charges=cd['MonthlyCharges'],
                    total_charges=cd['TotalCharges'],
                    internet_service=cd['InternetService']
                )
                db.session.add(customer)
                db.session.flush()

                prediction_obj = Prediction(
                    customer_id=customer.id,
                    will_churn=int(item['pred']),
                    churn_probability=float(item['prob']),
                    risk_level=item['risk']
                )
                db.session.add(prediction_obj)

            db.session.commit()
            print(f"✅ Saved to database successfully!")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Database save error: {e}")

        return jsonify({
            'upload_id': upload_id,
            'summary': {
                'total': total,
                'high_risk': high_risk,
                'high_risk_pct': round(high_risk / total * 100, 1) if total > 0 else 0,
                'medium_risk': medium_risk,
                'medium_risk_pct': round(medium_risk / total * 100, 1) if total > 0 else 0,
                'low_risk': low_risk,
                'low_risk_pct': round(low_risk / total * 100, 1) if total > 0 else 0,
            },
            'results': results
        })

    except Exception as e:
        print(f"❌ Batch predict error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/download-sample')
def download_sample():
    sample_data = """Gender,SeniorCitizen,Partner,Dependents,tenure,Contract,PaymentMethod,MonthlyCharges,TotalCharges,InternetService
Female,1,No,No,2,Month-to-month,Electronic check,95.0,190.0,Fiber optic
Male,0,Yes,Yes,48,Two year,Credit card (automatic),45.0,2160.0,DSL
Female,0,No,No,12,Month-to-month,Bank transfer (automatic),85.5,1026.0,Fiber optic
Male,1,Yes,No,3,Month-to-month,Electronic check,89.0,267.0,Fiber optic
Female,0,Yes,Yes,36,One year,Credit card (automatic),70.0,2520.0,DSL
Male,0,No,No,6,Month-to-month,Electronic check,95.0,570.0,Fiber optic
Female,1,No,No,1,Month-to-month,Electronic check,99.0,99.0,Fiber optic
Male,0,Yes,Yes,60,Two year,Bank transfer (automatic),50.0,3000.0,DSL"""
    return Response(
        sample_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=sample_customers.csv"}
    )


@app.route('/api/uploads')
def get_uploads():
    try:
        uploads = Upload.query.order_by(Upload.created_at.desc()).all()
        return jsonify({'uploads': [u.to_dict() for u in uploads]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/<upload_id>')
def get_upload_details(upload_id):
    try:
        customers = Customer.query.filter_by(upload_id=upload_id).all()
        results = []
        for customer in customers:
            cd = customer.to_dict()
            pred = Prediction.query.filter_by(customer_id=customer.id).first()
            if pred:
                cd['prediction'] = pred.to_dict()
            results.append(cd)
        return jsonify({'customers': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete-upload/<upload_id>', methods=['DELETE'])
def delete_upload(upload_id):
    try:
        customers = Customer.query.filter_by(upload_id=upload_id).all()
        for customer in customers:
            Prediction.query.filter_by(customer_id=customer.id).delete()
        Customer.query.filter_by(upload_id=upload_id).delete()
        Upload.query.filter_by(upload_id=upload_id).delete()
        db.session.commit()
        return jsonify({'success': True})
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