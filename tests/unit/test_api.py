import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import pandas as pd
from src.api.main import app

client = TestClient(app)

@pytest.fixture
def valid_payload():
    """Fournit un dictionnaire de données valides respectant PredictionInput."""
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
    
@patch('src.api.main.db_manager')
@patch('src.api.main.model')    # On mock le modèle pour éviter d'avoir à charger un vrai fichier .pkl
def test_predict_success(mock_model, mock_db_manager, valid_payload):
    """Test : Données valides -> Statut 200 et retour de la prédiction."""
    # Configuration du mock pour simuler le comportement du modèle de ML
    mock_model.predict.return_value = pd.Series([1500.50]).values
    mock_db_manager.save_prediction_input.return_value = 1
    
    response = client.post("/predict", json=valid_payload)
    
    assert response.status_code == 200
    assert "prediction" in response.json()
    assert response.json()["prediction"] == [1500.50]

    mock_model.predict.assert_called_once()
    mock_db_manager.save_prediction_input.assert_called_once_with(valid_payload)
    mock_db_manager.save_prediction_output.assert_called_once_with(1, 1500.50)

def test_predict_invalid_type(valid_payload):
    """Test : Données avec un mauvais type -> Statut 422 (Unprocessable Entity)."""
    invalid_payload = valid_payload.copy()    
    
    # On modifie un champ pour lui donner un mauvais type
    invalid_payload["NumberofFloors"] = "Cinq étages au lieu d'un int"
    
    response = client.post("/predict", json=invalid_payload)
    
    assert response.status_code == 422
    assert response.json()["Erreur"] == "Les données envoyées sont invalides ou incomplètes."
    assert response.json()["Détail"][0]["loc"] == ["body", "NumberofFloors"]

def test_predict_missing_data(valid_payload):
    """Test : Données manquantes (champ requis absent) -> Statut 422."""
    # On supprime un champ obligatoire
    del valid_payload["BuildingType"]
    
    response = client.post("/predict", json=valid_payload)
    
    assert response.status_code == 422
    assert response.json()["Erreur"] == "Les données envoyées sont invalides ou incomplètes."
    assert response.json()["Détail"][0]["loc"] == ["body", "BuildingType"]
    assert response.json()["Détail"][0]["msg"] == "Field required"

def test_predict_coherence_boundaries(valid_payload):
    """Test avec des valeurs aberrantes (ex: Nombre d'étages négatif)."""
    valid_payload["NumberofFloors"] = -5
    
    response = client.post("/predict", json=valid_payload)
    
    assert response.status_code == 422

@patch('src.api.main.db_manager')
@patch('src.api.main.model')
def test_predict_with_only_required_fields(mock_model, mock_db_manager):
    """Test que l'API fonctionne même si TOUS les champs optionnels sont omis."""
    minimal_payload = {
        "BuildingType": "Commercial",
        "PrimaryPropertyType": "Office",
        "Neighborhood": "Downtown",
        "YearBuilt": 2000,
        "NumberofFloors": 2,
        "PropertyGFAParking": 100,
        "PropertyGFABuildings": 2000,
        "ListOfAllPropertyUseTypes": "Office",
        "LargestPropertyUseType": "Office",
        "LargestPropertyUseTypeGFA": 2000.0,
        "ComplianceStatus": "Compliant"
    }
    
    mock_model.predict.return_value = pd.Series([42.0]).values
    mock_db_manager.save_prediction_input.return_value = 2
    
    response = client.post("/predict", json=minimal_payload)
        
    assert response.status_code == 200
    mock_db_manager.save_prediction_output.assert_called_once_with(2, 42.0)

@patch('src.api.main.db_manager')
@patch('src.api.main.apply_feature_engineering')
@patch('src.api.main.delete_useless_features')
@patch('src.api.main.model', new_callable=MagicMock)
def test_predict_empty_after_preprocessing(mock_model, mock_delete, mock_engineering, mock_db_manager, valid_payload):
    """Test si les données deviennent vides après filtrage -> Erreur 400."""    
    # On simule que le feature engineering retourne un DataFrame vide
    mock_delete.return_value = pd.DataFrame([valid_payload])
    mock_engineering.return_value = pd.DataFrame()
    mock_db_manager.save_prediction_input.return_value = 3

    response = client.post("/predict", json=valid_payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Les données d'entrée sont invalides après le prétraitement."

    mock_db_manager.save_prediction_output.assert_not_called()

@patch('src.api.main.db_manager')
@patch('src.api.main.model')
def test_predict_internal_server_error(mock_model, mock_db_manager, valid_payload):
    """Test si le modèle crash -> Erreur 500."""
    # On force le modèle à lever une erreur lors du .predict()
    mock_model.predict.side_effect = Exception("Crash interne du modèle ML")
    mock_db_manager.save_prediction_input.return_value = 4

    response = client.post("/predict", json=valid_payload)

    assert response.status_code == 500
    assert "Crash interne du modèle ML" in response.json()["detail"]

    mock_db_manager.save_prediction_output.assert_not_called()