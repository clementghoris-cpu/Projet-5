import joblib

def load_model(model_path: str):
    """
    Charge le modèle à partir du chemin spécifié.

    Args:
        model_path (str): Chemin vers le fichier du modèle sauvegardé.

    Returns:
        sklearn.pipeline.Pipeline: Pipeline de prétraitement et modèle chargé.
    """
    try:
        model = joblib.load(model_path)
        return model
    except FileNotFoundError:
        raise FileNotFoundError(f"Le fichier du modèle n'a pas été trouvé à l'emplacement spécifié : {model_path}")