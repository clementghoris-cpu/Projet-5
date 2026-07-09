import pytest
import pandas as pd
from unittest.mock import patch
from testcontainers.postgres import PostgresContainer
from src.database.db_manager import DatabaseManager
from src.database.models import Base, TrainData, PredictionInput, PredictionOutput

### --- FIXTURES POUR LES TESTS ---
@pytest.fixture(scope="session")
def postgres_container():
    """
    Démarre un conteneur PostgreSQL éphémère unique pour toute la session de test.
    """
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres

@pytest.fixture(scope="function")
def db_manager(postgres_container):
    """
    Fournit une instance de DatabaseManager connectée au conteneur de test.
    Recrée le schéma de base de données à blanc avant chaque test.
    """
    # Récupère l'URL de connexion dynamique du conteneur
    db_url = postgres_container.get_connection_url()

    # Force l'usage de Psycopg 3 (remplace postgresql+psycopg2 par postgresql+psycopg)
    if "+psycopg2" in db_url:
        db_url = db_url.replace("+psycopg2", "+psycopg")
    elif "postgresql://" in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://")
    
    with patch("src.project_config.database_config.DATABASE_URL", db_url):
        manager = DatabaseManager()        
        Base.metadata.create_all(bind=manager.engine)
        
        yield manager
        
        manager.close()
        Base.metadata.drop_all(bind=manager.engine)

### --- TESTS UNITAIRES ---
def test_get_training_data_nominal(db_manager):
    """Vérifie le chargement des données sous forme de DataFrame."""
    session = db_manager.Session()
    record = TrainData(
        OSEBuildingID=999,
        DataYear=2026,
        BuildingType="NonResidential",
        PrimaryPropertyType="Office",
        PropertyName="Lab Facility",
        Address="123 Science St",
        City="Seattle",
        State="WA",
        TaxParcelIdentificationNumber="1234567890",
        Neighborhood="Downtown",
        Latitude=47.6062,
        Longitude=-122.3321,
        YearBuilt=1995,
        NumberofFloors=5,
        PropertyGFATotal=50000,
        ListOfAllPropertyUseTypes="Office, Lab",
        LargestPropertyUseType="Office",
        LargestPropertyUseTypeGFA=40000.0,
        DefaultData=False,
        ComplianceStatus="Compliant"
    )
    session.add(record)
    session.commit()

    df = db_manager.get_training_data()
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.loc[0, "OSEBuildingID"] == 999
    assert df.loc[0, "PropertyName"] == "Lab Facility"

def test_get_training_data_empty_exception(db_manager):
    """Vérifie que la méthode lève bien une ValueError si aucune donnée n'est présente."""
    with pytest.raises(ValueError, match="Aucune donnée d'entraînement trouvée"):
        db_manager.get_training_data()

def test_save_prediction_input_nominal(db_manager):
    """Vérifie l'enregistrement des features d'entrée et la génération de l'ID."""
    payload = {
        "BuildingType": "Office",
        "PrimaryPropertyType": "Office",
        "Neighborhood": "Downtown",
        "YearBuilt": 2010,
        "NumberofFloors": 12,
        "ListOfAllPropertyUseTypes": "Office",
        "LargestPropertyUseType": "Office",
        "LargestPropertyUseTypeGFA": 25000.0,
        "ComplianceStatus": "Compliant"
    }
    
    input_id = db_manager.save_prediction_input(payload)
    
    assert isinstance(input_id, str)
    assert len(input_id) == 36  # Validation du format standard UUID v4
    
    # Double vérification en allant chercher directement en base
    session = db_manager.Session()
    saved = session.query(PredictionInput).filter_by(id=input_id).first()
    assert saved is not None
    assert saved.BuildingType == "Office"
    assert saved.NumberofFloors == 12

def test_save_prediction_output_nominal(db_manager):
    """Vérifie la liaison correcte et l'écriture de la prédiction finale."""
    payload = {
        "BuildingType": "Office",
        "PrimaryPropertyType": "Office",
        "Neighborhood": "Downtown",
        "YearBuilt": 2010,
        "NumberofFloors": 12,
        "ListOfAllPropertyUseTypes": "Office",
        "LargestPropertyUseType": "Office",
        "LargestPropertyUseTypeGFA": 25000.0,
        "ComplianceStatus": "Compliant"
    }
    input_id = db_manager.save_prediction_input(payload)
        
    output_id = db_manager.save_prediction_output(
        prediction_input_id=input_id,
        predicted_value=1250.75
    )
    
    session = db_manager.Session()
    saved_output = session.query(PredictionOutput).filter_by(id=output_id).first()
    
    assert saved_output is not None
    assert saved_output.predicted_value == 1250.75