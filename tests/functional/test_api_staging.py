import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.api.main import app
from src.project_config import database_config
from src.database.models import PredictionInput as DBInputModel, PredictionOutput as DBOutputModel

client = TestClient(app)

@patch("src.api.main.model")
def test_staging(mock_model):
    """
    Test End-to-End en Staging :
    Vérifie que l'API écrit réellement dans la base PostgreSQL et que les relations
    entre les tables d'input et d'output fonctionnent en conditions réelles.
    """    
    expected_prediction_value = 42.8542
    mock_model.predict.return_value = [expected_prediction_value]
    
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

    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    assert response.json() == {"prediction": [expected_prediction_value]}

    print(f"URL base de données : {database_config.DATABASE_URL}")

    engine = create_engine(database_config.DATABASE_URL)
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    saved_input = None
    saved_output = None

    try:
        assert response.status_code == 200
        assert response.json() == {"prediction": [expected_prediction_value]}

        saved_input = session.query(DBInputModel).filter_by(
            BuildingType="Commercial", 
            YearBuilt=1995
        ).order_by(DBInputModel.id.desc()).first()
        
        assert saved_input is not None
        
        saved_output = session.query(DBOutputModel).filter_by(prediction_input_id=saved_input.id).first()
        assert saved_output is not None
        assert pytest.approx(saved_output.predicted_value) == expected_prediction_value

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