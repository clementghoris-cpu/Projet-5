from datetime import datetime
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

def delete_missing_data_and_outliers(df_input : pd.DataFrame) -> pd.DataFrame:
    """
    /!\ utilisé pour le script d'entrainement du modèle uniquement /!\
    Supprime les lignes avec des valeurs manquantes et les outliers du DataFrame d'entrée.

    Args:
        df_input (pd.DataFrame): DataFrame d'entrée contenant les données brutes.

    Returns:
        pd.DataFrame: DataFrame avec les lignes contenant des valeurs manquantes et les outliers supprimés.
    """
    df = df_input.copy()

    # Suppression des lignes avec données manquantes
    df = df.dropna(subset=["ENERGYSTARScore", "SiteEUIWN(kBtu/sf)", "LargestPropertyUseTypeGFA", "LargestPropertyUseType"])

    # Suppression des lignes où LargestPropertyUseTypeGFA est plus grande que la surface totale PropertyGFATotal
    df = df[df["LargestPropertyUseTypeGFA"] <= df["PropertyGFATotal"]]

    # Suppression des valeurs impossibles
    df = df[(df["NumberofBuildings"] != 0) & (df["NumberofFloors"] > 0) & (df["NumberofFloors"] <= 76)]

    df = df[(df["Electricity(kBtu)"] >= 0) 
            & (df["SourceEUIWN(kBtu/sf)"] >= 0) 
            & (df["GHGEmissionsIntensity"] >= 0)]
    
    # Suppresion des lignes où 'Outlier' et 'ComplianceStatus' sont True
    df = df[df["Outlier"].isna()]
    df = df[df["ComplianceStatus"].str.lower() == "compliant"]

    # Suppression des outliers SiteEUIWN(kBtu/sf)
    Q1 = df["SiteEUIWN(kBtu/sf)"].quantile(0.25)
    Q3 = df["SiteEUIWN(kBtu/sf)"].quantile(0.75)
    
    IQR = Q3 - Q1    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    df = df[(df["SiteEUIWN(kBtu/sf)"] >= lower_bound) & (df["SiteEUIWN(kBtu/sf)"] <= upper_bound)]

    # Suppression des outliers GHGEmissionsIntensity
    Q1 = df["GHGEmissionsIntensity"].quantile(0.25)
    Q3 = df["GHGEmissionsIntensity"].quantile(0.75)

    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    df = df[(df["GHGEmissionsIntensity"] >= lower_bound) & (df["GHGEmissionsIntensity"] <= upper_bound)]

    return df


def delete_useless_features(df_input : pd.DataFrame) -> pd.DataFrame:
    """
    Supprime les colonnes inutiles du DataFrame d'entrée.

    Args:
        df_input (pd.DataFrame): DataFrame d'entrée contenant les données brutes.

    Returns:
        pd.DataFrame: DataFrame avec les colonnes inutiles supprimées.
    """
    df = df_input.copy()

    columns_to_drop = [
        "OSEBuildingID", "DataYear", "PropertyName", "Address", "City", "State", "ZipCode", "Latitude", "Longitude", 
        "TaxParcelIdentificationNumber", "CouncilDistrictCode", "YearsENERGYSTARCertified", "Comments", "DefaultData", 
        "Outlier", "ComplianceStatus", "PropertyGFATotal", "SiteEUI(kBtu/sf)", "SourceEUI(kBtu/sf)", "SourceEUIWN(kBtu/sf)",
        "SiteEnergyUse(kBtu)", "Electricity(kWh)", "SiteEnergyUseWN(kBtu)", "ListOfAllPropertyUseTypes", 
        "NaturalGas(therms)", "TotalGHGEmissions"        
    ]
    df = df.drop(columns=columns_to_drop, errors='ignore')
    
    return df

def apply_feature_engineering(df_input : pd.DataFrame) -> pd.DataFrame:
    """
    Applique les features engineering au DataFrame d'entrée.
    
    Args:
        df_input (pd.DataFrame): DataFrame d'entrée contenant les données brutes.

    Returns:
        pd.DataFrame: DataFrame avec les features engineering appliqués.
    """
    df = df_input.copy()

    # Feature BuildingAge
    df["BuildingAge"] = datetime.now().year - df["YearBuilt"]    
    df = df.drop(columns=["YearBuilt"])

    # Feature multi-usage
    df["IsMultiUsage"] = df.apply(lambda row: 1 if pd.notna(row["SecondLargestPropertyUseType"]) or pd.notna(row["ThirdLargestPropertyUseType"]) else 0, axis=1)

    # Remplissage des données manquantes 
    df["SecondLargestPropertyUseTypeGFA"] = df["SecondLargestPropertyUseTypeGFA"].fillna(0)
    df["ThirdLargestPropertyUseTypeGFA"] = df["ThirdLargestPropertyUseTypeGFA"].fillna(0)

    df["SecondLargestPropertyUseType"] = df["SecondLargestPropertyUseType"].fillna('NotUsed')
    df["ThirdLargestPropertyUseType"] = df["ThirdLargestPropertyUseType"].fillna('NotUsed')
 
    # Features surfaces ratio
    totalSurface = df["PropertyGFAParking"] + df["PropertyGFABuilding(s)"] # surface totale = parking + building

    ## Ratio surface parking  
    df["ParkingSurfaceRatio"] = df["PropertyGFAParking"] / totalSurface
    df["ParkingSurfaceRatio"].fillna(0, inplace=True) # Gère la division par 0 si jamais totalSurface =0

    ## Ratio surface largest property use type
    df["LargestUseSurfaceRatio"] = df["LargestPropertyUseTypeGFA"] / totalSurface
    df["LargestUseSurfaceRatio"].fillna(0, inplace=True)

    ## Ratio surface second largest property use type
    df["SecondLargestUseSurfaceRatio"] = df["SecondLargestPropertyUseTypeGFA"] / totalSurface
    df["SecondLargestUseSurfaceRatio"].fillna(0, inplace=True)

    ## Ratio surface third largest property use type
    df["ThirdLargestUseSurfaceRatio"] = df["ThirdLargestPropertyUseTypeGFA"] / totalSurface
    df["ThirdLargestUseSurfaceRatio"].fillna(0, inplace=True)

    # Feature Energies 
    df["HasElectricity"] = (df["Electricity(kBtu)"] > 0).astype(int)
    df["HasNaturalGas"] = (df["NaturalGas(kBtu)"] > 0).astype(int)
    df["HasSteam"] = (df["SteamUse(kBtu)"] > 0).astype(int)

    # Suppression des colonnes inutiles après le feature engineering
    df = df.drop(columns=[
        "Electricity(kBtu)", "NaturalGas(kBtu)", "SteamUse(kBtu)",
        "BuildingType", "PrimaryPropertyType",
        "SecondLargestPropertyUseType", "ThirdLargestPropertyUseType"
    ])

    return df

def build_preprocessor_pipeline(categorial_features: list, numerical_features: list):
    """
    Construit un pipeline de prétraitement pour les données.

    Args:
        categorial_features (list): Liste des noms de colonnes catégorielles.
        numerical_features (list): Liste des noms de colonnes numériques.

    Returns:
        ColumnTransformer: Pipeline de prétraitement.
    """   
    categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False, max_categories=15)
    numerical_transformer = StandardScaler()

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', categorical_transformer, categorial_features),
            ('num', numerical_transformer, numerical_features)
        ]
    )

    return preprocessor