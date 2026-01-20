import pickle
import pandas as pd
import numpy as np

class ChurnPredictor:
    def __init__(self):

        print("=" * 60)
        print("INITIALIZING CHURN PREDICTOR")
        print("=" * 60)
        
        print("\n1. Loading ensemble model...")
        try:
            with open('models/ensemble_model.pkl', 'rb') as f:
                self.ensemble = pickle.load(f)
            print("   ✅ Ensemble loaded")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise
        
        print("\n2. Loading scaler...")
        try:
            with open('models/scaler.pkl', 'rb') as f:
                self.scaler = pickle.load(f)
            print("   ✅ Scaler loaded")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise
        
        print("\n3. Loading label_encoders...")
        try:
            with open('models/label_encoders.pkl', 'rb') as f:
                self.label_encoders = pickle.load(f)
            print(f"   ✅ Label encoders loaded: {len(self.label_encoders)} encoders")
            print(f"   Encoders for: {list(self.label_encoders.keys())}")
        except Exception as e:
            print(f"   ❌ Error loading label_encoders: {e}")
            raise
        
        print("\n4. Loading feature names...")
        try:
            with open('models/feature_names.pkl', 'rb') as f:
                self.feature_names = pickle.load(f)
            print(f"   ✅ Feature names loaded: {len(self.feature_names)} features")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise
        
        print("\n5. Extracting individual models...")
        try:
            self.rf_model = self.ensemble['rf_model']
            self.gb_model = self.ensemble['gb_model']
            print("   ✅ Models extracted")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise
        
        print("\n" + "=" * 60)
        print("✅ INITIALIZATION COMPLETE!")
        print("=" * 60)
    
    def preprocess_input(self, customer_data):
        print("\n--- PREPROCESSING ---")
        
        # Create DataFrame
        df = pd.DataFrame([customer_data])
        print(f"Created DataFrame with {len(df.columns)} columns")
        
        # Handle TotalCharges
        if 'TotalCharges' in df.columns:
            df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
            df['TotalCharges'] = df['TotalCharges'].fillna(0)
        
        # Remove customerID
        if 'customerID' in df.columns:
            df = df.drop('customerID', axis=1)
        
        # Encode categorical
        print("Encoding categorical variables...")
        for col in df.select_dtypes(include=['object']).columns:
            print(f"  Encoding {col}...")
            if col in self.label_encoders:
                le = self.label_encoders[col]
                try:
                    df[col] = le.transform(df[col].astype(str))
                    print(f"    ✅ Encoded to: {df[col].values[0]}")
                except ValueError as e:
                    print(f"    ⚠️ Unknown value, using 0")
                    df[col] = 0
            else:
                print(f"    ⚠️ No encoder found for {col}")
        
        # Ensure all features
        for feature in self.feature_names:
            if feature not in df.columns:
                df[feature] = 0
        
        # Reorder
        df = df[self.feature_names]
        
        # Scale
        df_scaled = self.scaler.transform(df)
        print("✅ Preprocessing complete")
        
        return df_scaled
    
    def predict(self, customer_data):
        print("\n" + "=" * 60)
        print("MAKING PREDICTION")
        print("=" * 60)
        
        try:
            # Check if label_encoders exists
            if not hasattr(self, 'label_encoders'):
                raise AttributeError("label_encoders not found! This should never happen!")
            
            print(f"✅ label_encoders exists: {len(self.label_encoders)} encoders")
            
            # Preprocess
            X = self.preprocess_input(customer_data)
            
            # Predict
            rf_proba = self.rf_model.predict_proba(X)[0]
            gb_proba = self.gb_model.predict_proba(X)[0]
            
            # Ensemble
            ensemble_proba = (rf_proba + gb_proba) / 2
            churn_probability = ensemble_proba[1]
            
            # Risk level
            if churn_probability < 0.3:
                risk_level = "Low Risk"
                risk_color = "green"
            elif churn_probability < 0.6:
                risk_level = "Medium Risk"
                risk_color = "orange"
            elif churn_probability < 0.8:
                risk_level = "High Risk"
                risk_color = "red"
            else:
                risk_level = "Critical Risk"
                risk_color = "purple"
            
            # Feature importance
            feature_importance = []
            importances = self.rf_model.feature_importances_
            top_indices = importances.argsort()[-5:][::-1]
            
            for idx in top_indices:
                feature_importance.append({
                    'feature': self.feature_names[idx],
                    'value': float(X[0][idx]),
                    'importance': float(importances[idx])
                })
            
            print(f"\n✅ PREDICTION SUCCESSFUL!")
            print(f"   Probability: {churn_probability*100:.2f}%")
            print(f"   Risk: {risk_level}")
            
            return {
                'churn_probability': float(churn_probability),
                'risk_level': risk_level,
                'risk_color': risk_color,
                'will_churn': bool(churn_probability > 0.5),
                'confidence': float(max(ensemble_proba)),
                'feature_importance': feature_importance
            }
            
        except Exception as e:
            print(f"\n❌ PREDICTION FAILED: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("TESTING CHURN PREDICTOR")
    print("=" * 60)
    
    predictor = ChurnPredictor()
    
    test_customer = {
        'gender': 'Male',
        'SeniorCitizen': 0,
        'Partner': 'No',
        'Dependents': 'No',
        'tenure': 3,
        'PhoneService': 'Yes',
        'MultipleLines': 'No',
        'InternetService': 'Fiber optic',
        'OnlineSecurity': 'No',
        'OnlineBackup': 'No',
        'DeviceProtection': 'No',
        'TechSupport': 'No',
        'StreamingTV': 'No',
        'StreamingMovies': 'No',
        'Contract': 'Month-to-month',
        'PaperlessBilling': 'Yes',
        'PaymentMethod': 'Electronic check',
        'MonthlyCharges': 95.0,
        'TotalCharges': 285.0
    }
    
    result = predictor.predict(test_customer)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)