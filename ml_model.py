import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle
import os

MODEL_PATH = 'credit_score_model.pkl'

def train_model(data):
    """
    Trains a Random Forest model on the provided data.
    Data should be a list of dictionaries or a DataFrame with columns:
    ['year_2021', 'year_2022', 'year_2023', 'year_2024', 'year_2025', 'result']
    """
    df = pd.DataFrame(data)
    
    # Features and Target
    X = df[['year_2021', 'year_2022', 'year_2023', 'year_2024', 'year_2025']]
    y = df['result']
    
    # Train/Test Split (though we might just train on all for this simple app)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # Evaluate
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Save model
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(clf, f)
        
    return accuracy

def load_model():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    return None

def predict_credit_score(features):
    """
    Predicts if credit should be approved.
    Features: [y2021, y2022, y2023, y2024, y2025]
    """
    clf = load_model()
    if clf:
        # Reshape for single prediction
        return clf.predict([features])[0]
    else:
        # Fallback logic if model doesn't exist
        avg = sum(features) / len(features)
        return 1 if avg >= 0.8 else 0
