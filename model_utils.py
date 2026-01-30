import pandas as pd
import numpy as np

class ChurnPredictor:
    """Simple churn predictor with rule-based predictions"""
    
    def _init_(self):
        """Initialize the predictor"""
        print("ChurnPredictor initialized with rule-based predictions")
    
    def predict(self, customer_data):
        """
        Make a churn prediction for a single customer
        
        Args:
            customer_data: Dictionary with customer information
            
        Returns:
            prediction: 0 (will not churn) or 1 (will churn)
            probability: Probability of churning (0-1)
        """
        try:
            # Calculate risk score based on business rules
            risk_score = 0.3  # Base risk 30%
            
            # Contract type (biggest factor)
            contract = customer_data.get('Contract', '')
            if contract == 'Month-to-month':
                risk_score += 0.25
            elif contract == 'Two year':
                risk_score -= 0.20
            elif contract == 'One year':
                risk_score += 0.05
            
            # Tenure (how long they've been a customer)
            tenure = int(customer_data.get('tenure', 12))
            if tenure < 6:
                risk_score += 0.20
            elif tenure < 12:
                risk_score += 0.10
            elif tenure > 48:
                risk_score -= 0.15
            elif tenure > 24:
                risk_score -= 0.10
            
            # Monthly charges
            monthly_charges = float(customer_data.get('MonthlyCharges', 50))
            if monthly_charges > 90:
                risk_score += 0.12
            elif monthly_charges > 70:
                risk_score += 0.05
            elif monthly_charges < 30:
                risk_score -= 0.08
            
            # Senior citizen
            if int(customer_data.get('SeniorCitizen', 0)) == 1:
                risk_score += 0.08
            
            # Internet service
            internet = customer_data.get('InternetService', '')
            if internet == 'Fiber optic':
                risk_score += 0.05
            elif internet == 'No':
                risk_score -= 0.10
            
            # Partner and dependents (family stability)
            if customer_data.get('Partner', 'No') == 'Yes':
                risk_score -= 0.08
            if customer_data.get('Dependents', 'No') == 'Yes':
                risk_score -= 0.08
            
            # Payment method
            payment = customer_data.get('PaymentMethod', '')
            if 'Electronic check' in payment:
                risk_score += 0.10
            elif 'automatic' in payment.lower():
                risk_score -= 0.05
            
            # Ensure probability is between 0 and 1
            probability = max(0.05, min(0.95, risk_score))
            
            # Prediction based on threshold
            prediction = 1 if probability > 0.5 else 0
            
            return int(prediction), float(probability)
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            # Return safe default on error
            return 0, 0.5