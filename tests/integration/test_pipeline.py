import pytest
from unittest.mock import MagicMock
import pandas as pd
import numpy as np
from src.model.preprocessing import delete_useless_features, apply_feature_engineering

@pytest.fixture
def sample_input_dict():
    return {
        "BuildingType": "Commercial",
        "PrimaryPropertyType": "Office",
        "Neighborhood": "Downtown",
        "YearBuilt": 1995,
        "NumberofBuildings": 1.0,
        "NumberofFloors": 5,
        "PropertyGFAParking": 0,
        "PropertyGFABuildings": 50000,
        "ListOfAllPropertyUseTypes": "Office",
        "LargestPropertyUseType": "Office",
        "LargestPropertyUseTypeGFA": 50000.0,
        "SecondLargestPropertyUseType": None,
        "SecondLargestPropertyUseTypeGFA": None,
        "ThirdLargestPropertyUseType": None,
        "ThirdLargestPropertyUseTypeGFA": None,
        "ENERGYSTARScore": 85.0,
        "steam_use_kbtu": 0.0,            
        "electricity_kbtu": 120000.0,    
        "natural_gas_kbtu": 45000.0,      
        "ComplianceStatus": "Compliant",
        "Outlier": None,
        "GHGEmissionsIntensity": 1.2
    }


def test_pipeline_integration_preprocessing_to_model(sample_input_dict):
    """
    Vérifie que le dictionnaire d'entrée est correctement nettoyé, transformé
    par le Feature Engineering, et que le format obtenu est compatible avec scikit-learn.
    """    
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([40.8542])
    
    df_input = pd.DataFrame([sample_input_dict])
    
    df_cleaned = delete_useless_features(df_input)
    df_engineered = apply_feature_engineering(df_cleaned)

    # Vérifications intermédiaires sur le Feature Engineering
    assert "BuildingAge" in df_engineered.columns
    assert df_engineered.loc[0, "IsMultiUsage"] == 0
    assert df_engineered.loc[0, "HasElectricity"] == 1
    assert "YearBuilt" not in df_engineered.columns  # Doit être supprimé après le feature engineering
    
    prediction = mock_model.predict(df_engineered)

    # Assertions finales
    assert len(prediction) == 1
    assert isinstance(prediction[0], float)
    mock_model.predict.assert_called_once_with(df_engineered)