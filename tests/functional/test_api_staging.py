import os
import pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.project_config import database_config
from src.database.models import PredictionInput as DBInputModel, PredictionOutput as DBOutputModel

def test_staging_api_health():
    """
    Vérifie que l'API de Staging répond correctement et est 'Live'.
    """
    STAGING_API_URL = os.getenv("STAGING_API_URL", "http://localhost:8000")

    if not STAGING_API_URL:
        raise RuntimeError(
            "\n[ERREUR CRITIQUE] La variable d'environnement 'STAGING_API_URL' n'est pas définie ! "
            "Le test fonctionnel de Staging ne peut pas s'exécuter sans l'URL de l'API déployée."
        )

    response = requests.get(f"{STAGING_API_URL}/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data.get("Status") == "API is running"


def test_staging_api_predict():
    """
    Test End-to-End en Staging :
    Vérifie que l'API écrit réellement dans la base PostgreSQL et que les relations
    entre les tables d'input et d'output fonctionnent en conditions réelles.
    """    
    STAGING_API_URL = os.getenv("STAGING_API_URL", "http://localhost:8000")

    if not STAGING_API_URL:
        raise RuntimeError(
            "\n[ERREUR CRITIQUE] La variable d'environnement 'STAGING_API_URL' n'est pas définie ! "
            "Le test fonctionnel de Staging ne peut pas s'exécuter sans l'URL de l'API déployée."
        )
    
    payload = {
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
    
    response = requests.post(f"{STAGING_API_URL}/predict", json=payload)

    assert response.status_code == 200
    response_data = response.json()
    assert "prediction" in response_data 

    # Récupère la valeur prédite afin de la comparer avec ce qui a été enregistré dans la base de données
    predicted_value = response_data["prediction"][0]
    assert isinstance(predicted_value, (int, float))
   
    engine = create_engine(database_config.DATABASE_URL)
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    saved_input = None
    saved_output = None

    try:        
        saved_input = session.query(DBInputModel).filter_by(
            BuildingType="Commercial", 
            YearBuilt=1995
        ).order_by(DBInputModel.id.desc()).first()
        
        assert saved_input is not None
        
        saved_output = session.query(DBOutputModel).filter_by(prediction_input_id=saved_input.id).first()
        assert saved_output is not None
        assert pytest.approx(saved_output.predicted_value) == predicted_value

    finally:
        try:
            if saved_output:
                session.delete(saved_output)
            if saved_input:
                session.delete(saved_input)
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()
            Session.remove()