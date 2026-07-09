from datetime import datetime
import numpy as np
import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from src.model.preprocessing import apply_feature_engineering, build_preprocessor_pipeline, delete_missing_data_and_outliers, delete_useless_features

### --- FIXTURES POUR LES DONNÉES DE TEST ---
@pytest.fixture
def sample_raw_data():
    """Génère un DataFrame minimaliste représentant les données brutes."""
    return pd.DataFrame(
        {
            "ENERGYSTARScore": [80.0, np.nan, 95.0, 50.0],
            "SiteEUIWN_kBtu_sf": [10.0, 20.0, 15.0, 500.0],  # 500 sera un outlier
            "LargestPropertyUseTypeGFA": [1000, 1500, 2000, 1200],
            "PropertyGFATotal": [1200, 1500, 2500, 1500],  # Ligne 1: Largest > Total -> à supprimer
            "LargestPropertyUseType": ["Office", "Office", "Hotel", "Office"],
            "NumberofBuildings": [1, 1, 1, 1],
            "NumberofFloors": [5, 3, 2, 4],
            "electricity_kbtu": [100, 200, 300, 400],
            "SourceEUIWN_kBtu_sf": [12, 22, 32, 42],
            "GHGEmissionsIntensity": [1.2, 2.2, 3.2, 100.0], 
            "Outlier": [np.nan, np.nan, np.nan, np.nan],
            "ComplianceStatus": [
                "Compliant",
                "Compliant",
                "Compliant",
                "NotCompliant",
            ],
        }
    )

@pytest.fixture
def sample_engineering_data():
    """Génère un DataFrame propre pour tester le feature engineering."""
    return pd.DataFrame(
        {
            "SecondLargestPropertyUseTypeGFA": [np.nan, 200.0],
            "ThirdLargestPropertyUseTypeGFA": [100.0, np.nan],
            "SecondLargestPropertyUseType": [np.nan, "Retail"],
            "ThirdLargestPropertyUseType": ["Storage", np.nan],
            "YearBuilt": [2000, 2010],
            "PropertyGFAParking": [100, 0],
            "PropertyGFABuildings": [900, 1000],
            "LargestPropertyUseTypeGFA": [700, 800],
            "electricity_kbtu": [50, 0],
            "natural_gas_kbtu": [0, 30],
            "steam_use_kbtu": [10, 0],
            "BuildingType": ["NonResidential", "NonResidential"],
            "PrimaryPropertyType": ["Hotel", "Office"],
        }
    )


### --- TESTS UNITAIRES ---
def test_delete_missing_data_and_outliers(sample_raw_data):
    """Vérifie que les valeurs manquantes, les aberrations et les outliers sont bien filtrés."""
    # Act
    df_clean = delete_missing_data_and_outliers(sample_raw_data)

    # Assert
    # 1. La ligne avec ENERGYSTARScore NaN doit sauter (index 1)
    # 2. La ligne où LargestPropertyUseTypeGFA > PropertyGFATotal doit sauter (index 1, déjà visée)
    # 3. La ligne avec l'outlier à 500.0 en SiteEUIWN doit sauter (index 3)
    # Il ne devrait rester que la ligne d'index 0 et 2
    assert len(df_clean) == 2
    assert 0 in df_clean.index
    assert 2 in df_clean.index
    assert 1 not in df_clean.index
    assert 3 not in df_clean.index


def test_delete_useless_features():
    """Vérifie que les colonnes inutiles sont bien supprimées et qu'aucune erreur n'est levée si une colonne est absente."""
    # Arrange
    df = pd.DataFrame(
        {"OSEBuildingID": [1, 2], "FeatureUtile": [10, 20], "DataYear": [2016, 2016]}
    )

    # Act
    df_reduced = delete_useless_features(df)

    # Assert
    assert "FeatureUtile" in df_reduced.columns
    assert "OSEBuildingID" not in df_reduced.columns
    assert "DataYear" not in df_reduced.columns
    assert df_reduced.shape[1] == 1


def test_apply_feature_engineering(sample_engineering_data):
    """Vérifie le calcul des nouvelles features, le calcul des ratios et la suppression finale des colonnes."""
    # Act
    df_engineered = apply_feature_engineering(sample_engineering_data)

    # Assert - Validation du calcul de l'âge du bâtiment
    expected_age_0 = datetime.now().year - 2000
    assert df_engineered.loc[0, "BuildingAge"] == expected_age_0
    assert "YearBuilt" not in df_engineered.columns

    # Assert - Validation des ratios (Total surface = 100 + 900 = 1000 pour l'index 0)
    assert df_engineered.loc[0, "ParkingSurfaceRatio"] == 100 / 1000
    assert df_engineered.loc[0, "LargestUseSurfaceRatio"] == 700 / 1000

    # Assert - Validation des flags d'énergie (Index 0 a Electricity > 0 et SteamUse > 0)
    assert df_engineered.loc[0, "HasElectricity"] == 1
    assert df_engineered.loc[0, "HasNaturalGas"] == 0
    assert df_engineered.loc[0, "HasSteam"] == 1

    # Assert - Validation de la suppression des colonnes intermédiaires
    dropped_cols = [
        "electricity_kbtu",
        "BuildingType",
        "SecondLargestPropertyUseType",
    ]
    for col in dropped_cols:
        assert col not in df_engineered.columns


def test_build_preprocessor_pipeline():
    """Vérifie que le pipeline Scikit-Learn est correctement instancié."""
    # Arrange
    cat_features = ["Type"]
    num_features = ["Age", "Ratio"]

    # Act
    preprocessor = build_preprocessor_pipeline(cat_features, num_features)

    # Assert
    assert isinstance(preprocessor, ColumnTransformer)
    # Vérification qu'il y a bien 2 transformers définis ('cat' et 'num')
    transformer_names = [trans[0] for trans in preprocessor.transformers]
    assert "cat" in transformer_names
    assert "num" in transformer_names