import os

class DatabaseConfig:
    USER: str = os.getenv("POSTGRES_USER", "default_user")
    PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "default_password")
    HOST: str = os.getenv("POSTGRES_HOST", "db")
    PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    DB_NAME: str = os.getenv("POSTGRES_DB", "energy_db")
    DATABASE_URL: str = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

class ModelConfig:
    MODEL_PATH: str = os.path.join(os.getcwd(), "data", "model", "pipeline_model.pkl") # Ne pas utiliser de \ car lors du déploiement sur Linux, cela peut poser problème. Utiliser os.path.join pour la compatibilité multi-plateforme.

class APIConfig:
    DEBUG: bool = os.getenv("API_DEBUG", "False").lower() == "true"
    TITLE: str = "API prediction consommation énergétique"
    VERSION: str = "1.0"

database_config = DatabaseConfig()
model_config = ModelConfig()
api_config = APIConfig()