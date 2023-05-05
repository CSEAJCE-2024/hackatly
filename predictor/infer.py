import pandas as pd
import numpy as np
from joblib import load


def predict_disease(symptoms):
    # Prepare Test Data
    df_test = pd.DataFrame(columns=list(symptoms.keys()))
    df_test.loc[0] = np.array(list(symptoms.values()))

    # Load pre-trained model
    clf = load(str("predictor/saved_model/random_forest.joblib"))
    result = clf.predict(df_test)
    return result[0]
