import pandas as pd
import numpy as np


class ChurnPredictor:
    """Customer Churn Predictor using rule-based algorithm"""
    
    def _init_(self):
        """Initialize the predictor"""
        print("🤖 ChurnPredictor initialized with rule-based algorithm")
    
    def predict(self, customer_data):
        """
        Make a churn prediction for a single customer
        
        Args:
            customer_data (dict): Dictionary with customer attributes
        
        Returns:
            tuple: (prediction, probability)
                prediction (int): 0 = Will Stay, 1 = Will Churn
                probability (float): Churn probability (0.0 to 1.0)
        """
        try:
            # Initialize base risk score (30%)
            risk_score = 0.30
            
            # FACTOR 1: CONTRACT TYPE (Biggest Impact)
            contract = str(customer_data.get('Contract', '')).strip()
            
            if 'Month-to-month' in contract or 'month' in contract.lower():
                risk_score += 0.25  # +25% for month-to-month
            elif 'Two year' in contract or 'two' in contract.lower():
                risk_score -= 0.20  # -20% for two-year
            elif 'One year' in contract or 'one' in contract.lower():
                risk_score += 0.05  # +5% for one-year
            
            # FACTOR 2: TENURE (Customer loyalty)
            try:
                tenure = int(customer_data.get('tenure', 12))
            except (ValueError, TypeError):
                tenure = 12
            
            if tenure < 6:
                risk_score += 0.20  # Very new customer
            elif tenure < 12:
                risk_score += 0.10  # New customer
            elif tenure > 48:
                risk_score -= 0.15  # Long-term customer
            elif tenure > 24:
                risk_score -= 0.10  # Established customer
            
            # FACTOR 3: MONTHLY CHARGES (Price sensitivity)
            try:
                monthly_charges = float(customer_data.get('MonthlyCharges', 50))
            except (ValueError, TypeError):
                monthly_charges = 50
            
            if monthly_charges > 90:
                risk_score += 0.12  # High bills
            elif monthly_charges > 70:
                risk_score += 0.05  # Above average
            elif monthly_charges < 30:
                risk_score -= 0.08  # Budget-friendly
            
            # FACTOR 4: SENIOR CITIZEN
            try:
                senior = int(customer_data.get('SeniorCitizen', 0))
            except (ValueError, TypeError):
                senior = 0
            
            if senior == 1:
                risk_score += 0.08
            
            # FACTOR 5: INTERNET SERVICE
            internet = str(customer_data.get('InternetService', '')).strip()
            
            if 'Fiber' in internet or 'fiber' in internet.lower():
                risk_score += 0.05  # More competition
            elif internet == 'No' or 'no' in internet.lower():
                risk_score -= 0.10  # Simpler service
            
            # FACTOR 6: PARTNER (Family stability)
            partner = str(customer_data.get('Partner', 'No')).strip()
            if partner == 'Yes' or 'yes' in partner.lower():
                risk_score -= 0.08
            
            # FACTOR 7: DEPENDENTS
            dependents = str(customer_data.get('Dependents', 'No')).strip()
            if dependents == 'Yes' or 'yes' in dependents.lower():
                risk_score -= 0.08
            
            # FACTOR 8: PAYMENT METHOD
            payment = str(customer_data.get('PaymentMethod', '')).strip()
            
            if 'Electronic check' in payment or 'electronic' in payment.lower():
                risk_score += 0.10  # Manual payment
            elif 'automatic' in payment.lower() or 'auto' in payment.lower():
                risk_score -= 0.05  # Auto-payment
            
            # Ensure probability is between 5% and 95%
            probability = max(0.05, min(0.95, risk_score))
            
            # Binary prediction (threshold: 50%)
            prediction = 1 if probability > 0.5 else 0
            
            # IMPORTANT: Return as Python int and float (not numpy types)
            return int(prediction), float(probability)
            
        except Exception as e:
            print(f"⚠️ Prediction error: {e}")
            # Safe default: 50% probability, will stay
            return 0, 0.50
    
    def batch_predict(self, customers_list):
        """Make predictions for multiple customers"""
        predictions = []
        probabilities = []
        
        for customer_data in customers_list:
            pred, prob = self.predict(customer_data)
            predictions.append(pred)
            probabilities.append(prob)
        