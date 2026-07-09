import uuid
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import TrainData, PredictionInput, PredictionOutput
from src.project_config import database_config

class DatabaseManager:
    def __init__(self):        
        self.DATABASE_URL = database_config.DATABASE_URL                
        self.engine = create_engine(self.DATABASE_URL)       
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def get_training_data(self) -> pd.DataFrame:
        """
        Récupère toutes les données de la table train_data et les retourne sous forme de DataFrame.
        """
        session = self.Session()
        try:
            train_data = session.query(TrainData).all()

            if not train_data:
                raise ValueError("Aucune donnée d'entraînement trouvée dans la base de données.")

            # Conversion en DataFrame avec TOUTES les colonnes de TrainData
            df = pd.DataFrame([{
                "OSEBuildingID": td.OSEBuildingID,
                "DataYear": td.DataYear,
                "BuildingType": td.BuildingType,
                "PrimaryPropertyType": td.PrimaryPropertyType,
                "PropertyName": td.PropertyName,
                "Address": td.Address,
                "City": td.City,
                "State": td.State,
                "ZipCode": td.ZipCode,
                "TaxParcelIdentificationNumber": td.TaxParcelIdentificationNumber,
                "CouncilDistrictCode": td.CouncilDistrictCode,
                "Neighborhood": td.Neighborhood,
                "Latitude": td.Latitude,
                "Longitude": td.Longitude,
                "YearBuilt": td.YearBuilt,
                "NumberofBuildings": td.NumberofBuildings,
                "NumberofFloors": td.NumberofFloors,
                "PropertyGFATotal": td.PropertyGFATotal,
                "PropertyGFAParking": td.PropertyGFAParking,
                "property_gfa_buildings": td.property_gfa_buildings,
                "ListOfAllPropertyUseTypes": td.ListOfAllPropertyUseTypes,
                "LargestPropertyUseType": td.LargestPropertyUseType,
                "LargestPropertyUseTypeGFA": td.LargestPropertyUseTypeGFA,
                "SecondLargestPropertyUseType": td.SecondLargestPropertyUseType,
                "SecondLargestPropertyUseTypeGFA": td.SecondLargestPropertyUseTypeGFA,
                "ThirdLargestPropertyUseType": td.ThirdLargestPropertyUseType,
                "ThirdLargestPropertyUseTypeGFA": td.ThirdLargestPropertyUseTypeGFA,
                "YearsENERGYSTARCertified": td.YearsENERGYSTARCertified,
                "ENERGYSTARScore": td.ENERGYSTARScore,
                "steam_use_kbtu": td.steam_use_kbtu,
                "electricity_kwh": td.electricity_kwh,
                "electricity_kbtu": td.electricity_kbtu,
                "natural_gas_therms": td.natural_gas_therms,
                "natural_gas_kbtu": td.natural_gas_kbtu,
                "DefaultData": td.DefaultData,
                "Comments": td.Comments,
                "ComplianceStatus": td.ComplianceStatus,
                "Outlier": td.Outlier,
                "TotalGHGEmissions": td.TotalGHGEmissions,
                "GHGEmissionsIntensity": td.GHGEmissionsIntensity,
            } for td in train_data])

            return df
        finally:
            session.close()

    def save_prediction_input(self, input_data: dict) -> str:
        """
        Sauvegarde les données d'une requête de prédiction dans la table prediction_input.
        Retourne l'ID de l'entrée sauvegardée.
        """
        session = self.Session()
        try:
            prediction_input = PredictionInput(
                id=str(uuid.uuid4()),
                BuildingType=input_data.get("BuildingType"),
                PrimaryPropertyType=input_data.get("PrimaryPropertyType"),
                Neighborhood=input_data.get("Neighborhood"),
                YearBuilt=input_data.get("YearBuilt"),
                NumberofBuildings=input_data.get("NumberofBuildings"),
                NumberofFloors=input_data.get("NumberofFloors"),
                PropertyGFAParking=input_data.get("PropertyGFAParking"),
                property_gfa_buildings=input_data.get("property_gfa_buildings"),
                ListOfAllPropertyUseTypes=input_data.get("ListOfAllPropertyUseTypes"),
                LargestPropertyUseType=input_data.get("LargestPropertyUseType"),
                LargestPropertyUseTypeGFA=input_data.get("LargestPropertyUseTypeGFA"),
                SecondLargestPropertyUseType=input_data.get("SecondLargestPropertyUseType"),
                SecondLargestPropertyUseTypeGFA=input_data.get("SecondLargestPropertyUseTypeGFA"),
                ThirdLargestPropertyUseType=input_data.get("ThirdLargestPropertyUseType"),
                ThirdLargestPropertyUseTypeGFA=input_data.get("ThirdLargestPropertyUseTypeGFA"),
                ENERGYSTARScore=input_data.get("ENERGYSTARScore"),
                steam_use_kbtu=input_data.get("steam_use_kbtu"),
                electricity_kbtu=input_data.get("electricity_kbtu"),
                natural_gas_kbtu=input_data.get("natural_gas_kbtu"),
                ComplianceStatus=input_data.get("ComplianceStatus"),
                Outlier=input_data.get("Outlier"),
                GHGEmissionsIntensity=input_data.get("GHGEmissionsIntensity"),
            )

            session.add(prediction_input)
            session.commit()

            return prediction_input.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def save_prediction_output(self, prediction_input_id: str, predicted_value: float) -> str:
        """
        Sauvegarde le résultat de prédiction dans la table prediction_output.
        Retourne l'ID de l'entrée sauvegardée.
        """
        session = self.Session()
        try:
            prediction_output = PredictionOutput(
                id=str(uuid.uuid4()),
                prediction_input_id=prediction_input_id,
                predicted_value=predicted_value
            )
            session.add(prediction_output)
            session.commit()
            return prediction_output.id

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def close(self):
        """Ferme la session SQLAlchemy."""
        self.Session.remove()