from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Upload(db.Model):
    """Upload table to track CSV uploads"""
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
    """Customer table to store customer information"""
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
    """Prediction table to store prediction results"""
    _tablename_ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    will_churn = db.Column(db.Integer)
    churn_probability = db.Column(db.Float)
    risk_level = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
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