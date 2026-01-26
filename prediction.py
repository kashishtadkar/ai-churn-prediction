import pandas as pd
import numpy as np
import joblib
import os

class ChurnPredictor:
    def _init_(self):
        """Initialize the predictor and load models"""
        try:
            # Load the ensemble model
            self.ensemble_model = joblib.load('ensemble_model.pkl')
            self.scaler = joblib.load('scaler.pkl')
            self.label_encoders = joblib.load('label_encoders.pkl')
            self.feature_names = joblib.load('feature_names.pkl')
            print("✅ Models loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading models: {str(e)}")
            raise
    
    def preprocess_data(self, customer_data):
        """Preprocess customer data for prediction"""
        try:
            # Create DataFrame
            df = pd.DataFrame([customer_data])
            
            # Map categorical values
            # Gender
            df['Gender'] = df['Gender'].map({'Male': 1, 'Female': 0})
            
            # Partner and Dependents
            df['Partner'] = df['Partner'].map({'Yes': 1, 'No': 0})
            df['Dependents'] = df['Dependents'].map({'Yes': 1, 'No': 0})
            
            # Contract Type
            contract_mapping = {
                'Month-to-month': 0,
                'One year': 1,
                'Two year': 2
            }
            df['Contract'] = df['Contract'].map(contract_mapping)
            
            # Internet Service
            internet_mapping = {
                'No': 0,
                'DSL': 1,
                'Fiber optic': 2
            }
            df['InternetService'] = df['InternetService'].map(internet_mapping)
            
            # Payment Method
            payment_mapping = {
                'Electronic check': 0,
                'Mailed check': 1,
                'Bank transfer (automatic)': 2,
                'Credit card (automatic)': 3
            }
            df['PaymentMethod'] = df['PaymentMethod'].map(payment_mapping)
            
            # Convert to numeric
            numeric_columns = ['SeniorCitizen', 'tenure', 'MonthlyCharges', 'TotalCharges']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Fill any NaN values
            df = df.fillna(0)
            
            return df
            
        except Exception as e:
            print(f"Error in preprocessing: {str(e)}")
            raise
    
    def predict(self, customer_data):
        """
        Make prediction for a single customer
        Returns: (prediction, probability)
        """
        try:
            # Preprocess the data
            processed_data = self.preprocess_data(customer_data)
            
            # Get prediction (0 or 1)
            prediction = self.ensemble_model.predict(processed_data)[0]
            
            # Get probability
            try:
                probabilities = self.ensemble_model.predict_proba(processed_data)[0]
                # probabilities[1] = probability of churn (class 1)
                churn_probability = float(probabilities[1])
            except Exception as prob_error:
                print(f"⚠️ Probability calculation issue: {str(prob_error)}")
                # Fallback: if prediction is 1 (churn), use higher probability
                churn_probability = 0.75 if prediction == 1 else 0.25
            
            # Ensure probability is between 0 and 1
            churn_probability = max(0.0, min(1.0, churn_probability))
            
            print(f"✅ Prediction: {prediction}, Probability: {churn_probability:.2%}")
            
            return int(prediction), float(churn_probability)
            
        except Exception as e:
            print(f"❌ Error in prediction: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return safe default values
            return 0, 0.5
    
    def predict_batch(self, customers_df):
        """
        Make predictions for multiple customers
        Returns: DataFrame with predictions and probabilities
        """
        try:
            predictions = []
            probabilities = []
            
            for idx, row in customers_df.iterrows():
                customer_data = row.to_dict()
                pred, prob = self.predict(customer_data)
                predictions.append(pred)
                probabilities.append(prob)
            
            customers_df['Prediction'] = predictions
            customers_df['ChurnProbability'] = probabilities
            customers_df['RiskLevel'] = customers_df['ChurnProbability'].apply(
                lambda x: 'High' if x > 0.7 else ('Medium' if x > 0.3 else 'Low')
            )
            
            return customers_df
            
        except Exception as e:
            print(f"Error in batch prediction: {str(e)}")
            raise

# Test function
if __name__== "__main__":
    print("Testing ChurnPredictor...")
    predictor = ChurnPredictor()
    
    # Test with sample data
    test_customer = {
        'Gender': 'Male',
        'SeniorCitizen': 0,
        'Partner': 'No',
        'Dependents': 'No',
        'tenure': 2,
        'Contract': 'Month-to-month',
        'PaymentMethod': 'Electronic check',
        'MonthlyCharges': 89.0,
        'TotalCharges': 178.0,
        'InternetService': 'Fiber optic'
    }
    
    prediction, probability = predictor.predict(test_customer)
    print(f"\nTest Result:")
    print(f"Prediction: {'Churn' if prediction == 1 else 'Stay'}")
    print(f"Probability: {probability:.2%}")