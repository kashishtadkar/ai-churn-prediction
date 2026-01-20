import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
import pickle
import os

print("🚀 Starting Customer Churn Model Training...")

# Create models directory
if not os.path.exists('models'):
    os.makedirs('models')
    print("✅ Created 'models' folder")

# Load dataset
print("\n📂 Loading dataset...")
df = pd.read_csv('customer_data.csv')
print(f"✅ Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

# DATA CLEANING
print("\n🧹 Cleaning data...")
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df['TotalCharges'].fillna(df['TotalCharges'].median(), inplace=True)

if 'customerID' in df.columns:
    df = df.drop('customerID', axis=1)

df['Churn'] = df['Churn'].map({'Yes': 1, 'No': 0})
print("✅ Data cleaning completed!")

# FEATURE ENGINEERING
print("\n⚙️ Engineering features...")

# Store categorical columns BEFORE encoding
categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
print(f"   Found {len(categorical_cols)} categorical columns: {categorical_cols}")

# Create and save label encoders
label_encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le
    print(f"   ✓ Encoded {col}: {len(le.classes_)} unique values")

# Save label encoders IMMEDIATELY
with open('models/label_encoders.pkl', 'wb') as f:
    pickle.dump(label_encoders, f)
print(f"\n✅ Saved {len(label_encoders)} label encoders to models/label_encoders.pkl")

# SPLIT DATA
print("\n📊 Splitting data...")
X = df.drop('Churn', axis=1)
y = df['Churn']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Save feature names
feature_names = X.columns.tolist()
with open('models/feature_names.pkl', 'wb') as f:
    pickle.dump(feature_names, f)
print(f"✅ Saved {len(feature_names)} feature names")

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Save scaler
with open('models/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print("✅ Saved scaler")

print(f"\n   Training set: {X_train.shape[0]} samples")
print(f"   Test set: {X_test.shape[0]} samples")

# TRAIN MODELS
print("\n🤖 Training AI models...")

# Random Forest
print("\n1️⃣ Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train_scaled, y_train)
rf_pred = rf_model.predict(X_test_scaled)
rf_accuracy = accuracy_score(y_test, rf_pred)
print(f"   ✅ Random Forest Accuracy: {rf_accuracy*100:.2f}%")

# Gradient Boosting
print("\n2️⃣ Training Gradient Boosting...")
gb_model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42
)
gb_model.fit(X_train_scaled, y_train)
gb_pred = gb_model.predict(X_test_scaled)
gb_accuracy = accuracy_score(y_test, gb_pred)
print(f"   ✅ Gradient Boosting Accuracy: {gb_accuracy*100:.2f}%")

# ENSEMBLE
print("\n3️⃣ Creating Ensemble Model...")
ensemble_pred_proba = (rf_model.predict_proba(X_test_scaled) + 
                       gb_model.predict_proba(X_test_scaled)) / 2
ensemble_pred = (ensemble_pred_proba[:, 1] > 0.5).astype(int)
ensemble_accuracy = accuracy_score(y_test, ensemble_pred)

print(f"   ✅ Ensemble Accuracy: {ensemble_accuracy*100:.2f}%")

# EVALUATE
print("\n📈 Final Model Performance:")
precision = precision_score(y_test, ensemble_pred)
recall = recall_score(y_test, ensemble_pred)
auc_roc = roc_auc_score(y_test, ensemble_pred_proba[:, 1])

print(f"   📊 Accuracy:  {ensemble_accuracy*100:.2f}%")
print(f"   🎯 Precision: {precision*100:.2f}%")
print(f"   🔍 Recall:    {recall*100:.2f}%")
print(f"   📉 AUC-ROC:   {auc_roc*100:.2f}%")

# SAVE MODELS
print("\n💾 Saving models...")

# Save individual models
with open('models/rf_model.pkl', 'wb') as f:
    pickle.dump(rf_model, f)
print("   ✓ Saved Random Forest model")

with open('models/gb_model.pkl', 'wb') as f:
    pickle.dump(gb_model, f)
print("   ✓ Saved Gradient Boosting model")

# Save ensemble
ensemble_config = {
    'rf_model': rf_model,
    'gb_model': gb_model,
    'accuracy': ensemble_accuracy,
    'precision': precision,
    'recall': recall,
    'auc_roc': auc_roc
}

with open('models/ensemble_model.pkl', 'wb') as f:
    pickle.dump(ensemble_config, f)
print("   ✓ Saved Ensemble model")

# FEATURE IMPORTANCE
print("\n🔑 Top 10 Important Features:")
feature_importance = pd.DataFrame({
    'feature': feature_names,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

for idx, row in feature_importance.head(10).iterrows():
    print(f"   {row['feature']}: {row['importance']:.4f}")

print("\n" + "="*60)
print("🎉 MODEL TRAINING COMPLETED SUCCESSFULLY!")
print("="*60)
print("\n📁 Saved files in 'models/' folder:")
print("   ✅ ensemble_model.pkl")
print("   ✅ rf_model.pkl")
print("   ✅ gb_model.pkl")
print("   ✅ scaler.pkl")
print("   ✅ label_encoders.pkl")
print("   ✅ feature_names.pkl")
print("\n✅ Ready to make predictions!")
print("="*60)