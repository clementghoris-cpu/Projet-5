import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.project_config import model_config, api_config
from .schemas import PredictionInput
from src.model.model_loader import load_model
from src.model.preprocessing import delete_useless_features, apply_feature_engineering
from src.database.db_manager import DatabaseManager

model = load_model(model_config.MODEL_PATH)
app = FastAPI(title=api_config.TITLE, version=api_config.VERSION, debug=api_config.DEBUG)
db_manager = DatabaseManager()

# Exceptions handlers

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request : Request, exc : RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "Erreur": "Les données envoyées sont invalides ou incomplètes.",
            "Détail": exc.errors() 
            },
    )

#Routes

@app.get("/health", 
         summary="Vérifie l'état de santé de l'API",
         description="Cette route permet de vérifier si l'API est opérationnelle et retourne un message de bienvenue.",
         response_description="Message indiquant que l'API est en cours d'exécution.")
async def health_check():
    return {
        "Status": "API is running", 
        "Version": f"{app.version}", 
        "Message": "Welcome to the Energy Consumption Prediction API!"
    }

@app.post("/predict",
          summary="Prédis la consommation énergétique",
          description="Cette route prend en entrée les données nécessaires pour prédire la consommation énergétique et retourne la prédiction.",
          response_description="La prédiction de la consommation énergétique.")
async def predict(input_data: PredictionInput):
    try:
        print("Données d'entrée reçues pour la prédiction :")
        input_dict = input_data.model_dump(by_alias=True)   

        prediction_input_id = db_manager.save_prediction_input(input_dict)

        print("Données d'entrée après conversion en dictionnaire :")     
        df_input = pd.DataFrame([input_dict])

        print("prétraitement des données d'entrée :")
        # Prétraitement des données
        df_cleaned = delete_useless_features(df_input)

        print("Application du feature engineering :")
        df_engineered = apply_feature_engineering(df_cleaned)
       
        if df_engineered.empty:
            raise HTTPException(status_code=400, detail="Les données d'entrée sont invalides après le prétraitement.")
    
        print("Prédiction:")
        prediction = model.predict(df_engineered)

        db_manager.save_prediction_output(prediction_input_id, float(prediction[0]))

        return {"prediction": prediction.tolist()}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))