import joblib
import pandas as pd
import numpy as np
from pathlib import Path

class ChurnPredictor:
    """Class to handle churn predictions"""
    
    def _init_(self):
        """Initialize the predictor with the trained model"""
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model from file"""
        try:
            model_path = Path('churn_model.pkl')
            if model_path.exists():
                self.model = joblib.load(model_path)
                print("Model loaded successfully!")
            else:
                print("Warning: Model file not found. Using dummy predictions.")
                self.model = None
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def preprocess_data(self, customer_data):
        """Preprocess customer data for prediction"""
        # Create a dataframe with the customer data
        df = pd.DataFrame([customer_data])
        
        # Encoding categorical variables
        gender_map = {'Male': 1, 'Female': 0}
        yes_no_map = {'Yes': 1, 'No': 0}
        contract_map = {'Month-to-month': 0, 'One year': 1, 'Two year': 2}
        
        # Apply mappings
        df['Gender'] = df['Gender'].map(gender_map)
        df['Partner'] = df['Partner'].map(yes_no_map)
        df['Dependents'] = df['Dependents'].map(yes_no_map)
        df['Contract'] = df['Contract'].map(contract_map)
        
        # Handle InternetService
        if 'InternetService' in df.columns:
            internet_map = {'DSL': 1, 'Fiber optic': 2, 'No': 0}
            df['InternetService'] = df['InternetService'].map(internet_map)
        
        # Select features in the correct order
        feature_columns = [
            'Gender', 'SeniorCitizen', 'Partner', 'Dependents', 
            'tenure', 'Contract', 'MonthlyCharges', 'TotalCharges'
        ]
        
        # Add InternetService if exists
        if 'InternetService' in df.columns:
            feature_columns.append('InternetService')
        
        # Create feature array
        features = df[feature_columns].values
        
        return features
    
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
            # Preprocess the data
            features = self.preprocess_data(customer_data)
            
            # Make prediction
            if self.model is not None:
                prediction = self.model.predict(features)[0]
                probability = self.model.predict_proba(features)[0][1]
            else:
                # Dummy prediction based on simple rules when model is not available
                prediction, probability = self._dummy_predict(customer_data)
            
            return int(prediction), float(probability)
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            # Return default values on error
            return 0, 0.5
    
    def _dummy_predict(self, customer_data):
        """
        Create a dummy prediction when model is not available
        Based on simple business rules
        """
        risk_score = 0.3  # Base risk
        
        # Increase risk for month-to-month contracts
        if customer_data.get('Contract') == 'Month-to-month':
            risk_score += 0.2
        
        # Increase risk for low tenure
        if customer_data.get('tenure', 0) < 12:
            risk_score += 0.15
        
        # Increase risk for high monthly charges
        if customer_data.get('MonthlyCharges', 0) > 80:
            risk_score += 0.1
        
        # Increase risk for senior citizens
        if customer_data.get('SeniorCitizen', 0) == 1:
            risk_score += 0.1
        
        # Decrease risk for long tenure
        if customer_data.get('tenure', 0) > 48:
            risk_score -= 0.2
        
        # Decrease risk for two-year contract
        if customer_data.get('Contract') == 'Two year':
            risk_score -= 0.15
        
        # Ensure probability is between 0 and 1
        probability = max(0.0, min(1.0, risk_score))
        
        # Prediction based on threshold
        prediction = 1 if probability > 0.5 else 0
        
        return prediction, probability
    
    def batch_predict(self, customers_data):
        """
        Make predictions for multiple customers
        
        Args:
            customers_data: List of customer dictionaries
            
        Returns:
            predictions: List of predictions
            probabilities: List of probabilities
        """
        predictions = []
        probabilities = []
        
        for customer_data in customers_data:
            pred, prob = self.predict(customer_data)
            predictions.append(pred)
            probabilities.append(prob)
        
        return predictions, probabilities