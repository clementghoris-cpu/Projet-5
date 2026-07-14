import os
from src.database.models import Base, TrainData
import pandas as pd
from src.project_config import database_config, train_config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(database_config.DATABASE_URL)
Base.metadata.create_all(bind=engine)

def is_train_data_empty():
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        count = session.query(TrainData).count()
        return count == 0
    finally:
        session.close()

def insert_train_data_from_csv():
    if not os.path.exists(train_config.TRAIN_DATA_CSV_PATH):
        print(f"Le fichier CSV '{train_config.TRAIN_DATA_CSV_PATH}' n'existe pas.")
        return
    
    df = pd.read_csv(train_config.TRAIN_DATA_CSV_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        for _, row in df.iterrows():
            train_data = TrainData(
                OSEBuildingID=row['OSEBuildingID'],
                DataYear=row['DataYear'],
                BuildingType=row['BuildingType'],
                PrimaryPropertyType=row['PrimaryPropertyType'],
                PropertyName=row['PropertyName'],
                Address=row['Address'],
                City=row['City'],
                State=row['State'],
                ZipCode=row['ZipCode'] if not pd.isna(row['ZipCode']) else None,
                TaxParcelIdentificationNumber=row['TaxParcelIdentificationNumber'],
                CouncilDistrictCode=row['CouncilDistrictCode'] if not pd.isna(row['CouncilDistrictCode']) else None,
                Neighborhood=row['Neighborhood'],
                Latitude=row['Latitude'],
                Longitude=row['Longitude'],
                YearBuilt=row['YearBuilt'],
                NumberofBuildings=row['NumberofBuildings'] if not pd.isna(row['NumberofBuildings']) else None,
                NumberofFloors=row['NumberofFloors'],
                PropertyGFATotal=row['PropertyGFATotal'],
                PropertyGFAParking=row['PropertyGFAParking'] if not pd.isna(row['PropertyGFAParking']) else None,
                PropertyGFABuildings=row['PropertyGFABuildings'] if not pd.isna(row['PropertyGFABuildings']) else None,
                ListOfAllPropertyUseTypes=row['ListOfAllPropertyUseTypes'],
                LargestPropertyUseType=row['LargestPropertyUseType'],
                LargestPropertyUseTypeGFA=row['LargestPropertyUseTypeGFA'],
                SecondLargestPropertyUseType=row['SecondLargestPropertyUseType'] if not pd.isna(row['SecondLargestPropertyUseType']) else None,
                SecondLargestPropertyUseTypeGFA=row['SecondLargestPropertyUseTypeGFA'] if not pd.isna(row['SecondLargestPropertyUseTypeGFA']) else None,
                ThirdLargestPropertyUseType=row['ThirdLargestPropertyUseType'] if not pd.isna(row['ThirdLargestPropertyUseType']) else None,
                ThirdLargestPropertyUseTypeGFA=row['ThirdLargestPropertyUseTypeGFA'] if not pd.isna(row['ThirdLargestPropertyUseTypeGFA']) else None,
                YearsENERGYSTARCertified=row['YearsENERGYSTARCertified'] if not pd.isna(row['YearsENERGYSTARCertified']) else None,
                ENERGYSTARScore=row['ENERGYSTARScore'] if not pd.isna(row['ENERGYSTARScore']) else None,
                SiteEUI_kBtu_sf=row['SiteEUI_kBtu_sf'] if not pd.isna(row['SiteEUI_kBtu_sf']) else None,
                SiteEUIWN_kBtu_sf=row['SiteEUIWN_kBtu_sf'] if not pd.isna(row['SiteEUIWN_kBtu_sf']) else None,
                SourceEUI_kBtu_sf=row['SourceEUI_kBtu_sf'] if not pd.isna(row['SourceEUI_kBtu_sf']) else None,
                SourceEUIWN_kBtu_sf=row['SourceEUIWN_kBtu_sf'] if not pd.isna(row['SourceEUIWN_kBtu_sf']) else None,
                SiteEnergyUse_kBtu=row['SiteEnergyUse_kBtu'] if not pd.isna(row['SiteEnergyUse_kBtu']) else None,
                SiteEnergyUseWN_kBtu=row['SiteEnergyUseWN_kBtu'] if not pd.isna(row['SiteEnergyUseWN_kBtu']) else None,                
                steam_use_kbtu=row['steam_use_kbtu'] if not pd.isna(row['steam_use_kbtu']) else None,
                electricity_kwh=row['electricity_kwh'] if not pd.isna(row['electricity_kwh']) else None,
                electricity_kbtu=row['electricity_kbtu'] if not pd.isna(row['electricity_kbtu']) else None,
                natural_gas_therms=row['natural_gas_therms'] if not pd.isna(row['natural_gas_therms']) else None,
                natural_gas_kbtu=row['natural_gas_kbtu'] if not pd.isna(row['natural_gas_kbtu']) else None,
                DefaultData=row['DefaultData'] if not pd.isna(row['DefaultData']) else None,
                Comments=row['Comments'] if not pd.isna(row['Comments']) else None,
                ComplianceStatus=row['ComplianceStatus'] if not pd.isna(row['ComplianceStatus']) else None,
                Outlier=row['Outlier'] if not pd.isna(row['Outlier']) else None,
                TotalGHGEmissions=row['TotalGHGEmissions'] if not pd.isna(row['TotalGHGEmissions']) else None,
                GHGEmissionsIntensity=row['GHGEmissionsIntensity'] if not pd.isna(row['GHGEmissionsIntensity']) else None
            )

            session.add(train_data)
        session.commit()
        print("Données insérées avec succès.")
    except Exception as e:
        session.rollback()
        print(f"Erreur lors de l'insertion des données : {e}")
    finally:
        session.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès.")

    if is_train_data_empty():
        print("La table 'train_data' est vide. Insertion des données depuis le fichier CSV...")
        insert_train_data_from_csv()        

if __name__ == "__main__":
    init_db()