import joblib
import numpy as np
#import pandas as pd
import preprocessing
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from src.database.db_manager import DatabaseManager
#from src.project_config import train_config, model_config
from src.project_config import model_config

def run_model_training():
    """
    Exécute l'entraînement du modèle et sauvegarde le pipeline de prétraitement 
    et le modèle entraîné dans des fichiers.
    """
    db_manager = DatabaseManager()

    try:    
        print("Chargement des données...")
        # Lecture des données d'entrainement via le fichier CSV
        #df_raw = pd.read_csv(train_config.TRAIN_DATA_CSV_PATH)

        # Lecture des données d'entrainement via la base de données
        df_raw = db_manager.get_training_data()

        # 1. Nettoyage des features inutiles
        print("Nettoyage des features inutiles...")
        df_raw = preprocessing.delete_missing_data_and_outliers(df_raw)
        df_raw = preprocessing.delete_useless_features(df_raw)

        # 2. Split valeur cible et features
        print("Séparation de la valeur cible et des features...")
        X = df_raw.drop(columns=["SiteEUIWN_kBtu_sf"])
        y = df_raw["SiteEUIWN_kBtu_sf"]

        # 3. Application du feature engineering
        print("Application du feature engineering...")
        X_engineered = preprocessing.apply_feature_engineering(X)
        
        # 4. Définition des features catégorielles et numériques
        categorical_features = ["LargestPropertyUseType"]
        numerical_features = ["NumberofBuildings", "NumberofFloors", "PropertyGFAParking", "PropertyGFABuildings", 
                            "LargestPropertyUseTypeGFA", "SecondLargestPropertyUseTypeGFA", 
                            "ThirdLargestPropertyUseTypeGFA", "ENERGYSTARScore", "BuildingAge"]

        # 5. Création du pipeline prétraitement + modèle 
        print("Création du pipeline de prétraitement et du modèle...")
        preprocessor = preprocessing.build_preprocessor_pipeline(categorical_features, numerical_features)
        base_model = RandomForestRegressor(n_estimators=400, max_depth=10, min_samples_leaf=2, min_samples_split=5, random_state=42)
        model_with_log = TransformedTargetRegressor(regressor=base_model, func=np.log1p, inverse_func=np.expm1)

        pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', model_with_log)])

        # 6. Split des données en train et test
        print("Séparation des données en train et test...")
        X_train, X_test, y_train, y_test = train_test_split(X_engineered, y, test_size=0.2, random_state=42)

        # 7. Entraînement du modèle
        print("Entraînement du modèle...")
        pipeline.fit(X_train, y_train)
        
        # 8. Évaluation du modèle
        print("Évaluation du modèle...")
        y_pred = pipeline.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)

        print(f"Mean Squared Error: {mse}")
        print(f"Mean Absolute Error: {mae}")
        print(f"R² Score: {r2}")

        # 9. Sauvegarde du pipeline et du modèle
        print("Sauvegarde du pipeline et du modèle...")
        joblib.dump(pipeline, model_config.MODEL_PATH)
    except Exception as e:
        print(f"Erreur survenue lors de l'entrainement du modèle : {e}")
    finally:
        db_manager.close() 
        print("Entrainement modèle terminé...")

if __name__ == "__main__":
    run_model_training()