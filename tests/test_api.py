import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import pandas as pd
from api.main import app

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
        "PropertyGFABuilding(s)": 50000, 
        "ListOfAllPropertyUseTypes": "Office",
        "LargestPropertyUseType": "Office",
        "LargestPropertyUseTypeGFA": 50000.0,
        "SecondLargestPropertyUseType": None,
        "SecondLargestPropertyUseTypeGFA": None,
        "ThirdLargestPropertyUseType": None,
        "ThirdLargestPropertyUseTypeGFA": None,
        "ENERGYSTARScore": 85.0,
        "SteamUse(kBtu)": 0.0,            
        "Electricity(kBtu)": 120000.0,    
        "NaturalGas(kBtu)": 45000.0,      
        "ComplianceStatus": "Compliant",
        "Outlier": None,
        "GHGEmissionsIntensity": 1.2
    }
    
@patch('api.main.model')    # On mock le modèle pour éviter d'avoir à charger un vrai fichier .pkl
def test_predict_success(mock_model, valid_payload):
    """Test : Données valides -> Statut 200 et retour de la prédiction."""
    # Configuration du mock pour simuler le comportement du modèle de ML
    mock_model.predict.return_value = pd.Series([1500.50]).values # ou np.array
    
    response = client.post("/predict", json=valid_payload)
    
    assert response.status_code == 200
    assert "prediction" in response.json()
    assert response.json()["prediction"] == [1500.50]
    mock_model.predict.assert_called_once()

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

def test_predict_with_only_required_fields():
    """Test que l'API fonctionne même si TOUS les champs optionnels sont omis."""
    minimal_payload = {
        "BuildingType": "Commercial",
        "PrimaryPropertyType": "Office",
        "Neighborhood": "Downtown",
        "YearBuilt": 2000,
        "NumberofFloors": 2,
        "PropertyGFAParking": 100,
        "PropertyGFABuilding(s)": 2000,
        "ListOfAllPropertyUseTypes": "Office",
        "LargestPropertyUseType": "Office",
        "LargestPropertyUseTypeGFA": 2000.0,
        "ComplianceStatus": "Compliant"
    }
    
    with patch('api.main.model') as mock_model:
        mock_model.predict.return_value = pd.Series([42.0]).values
        response = client.post("/predict", json=minimal_payload)
        
        assert response.status_code == 200

@patch('api.main.apply_feature_engineering')
@patch('api.main.delete_useless_features')
def test_predict_empty_after_preprocessing(mock_delete, mock_engineering, valid_payload):
    """Test si les données deviennent vides après filtrage -> Erreur 400."""
    # On simule que le feature engineering retourne un DataFrame vide
    mock_delete.return_value = pd.DataFrame([valid_payload])
    mock_engineering.return_value = pd.DataFrame()  # Vide !

    response = client.post("/predict", json=valid_payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Les données d'entrée sont invalides après le prétraitement."

@patch('api.main.model')
def test_predict_internal_server_error(mock_model, valid_payload):
    """Test si le modèle crash -> Erreur 500."""
    # On force le modèle à lever une erreur lors du .predict()
    mock_model.predict.side_effect = Exception("Crash interne du modèle ML")

    response = client.post("/predict", json=valid_payload)

    assert response.status_code == 500
    assert "Crash interne du modèle ML" in response.json()["detail"]