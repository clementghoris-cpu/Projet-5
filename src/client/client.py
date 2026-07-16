import streamlit as st
import requests
import json

# Configuration de la page
st.set_page_config(page_title="Predicteur Énergie", layout="centered")


# Définition des jeux de données d'exemple
SAMPLES = {
    "Exemple 1 : Payload Complet (Office)": {
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
    },
    "Exemple 2 : Payload Minimal": {
        "BuildingType": "NonResidential",
        "PrimaryPropertyType": "Warehouse",
        "Neighborhood": "CENTRAL",
        "YearBuilt": 1965,
        "NumberofBuildings": 1.0,
        "NumberofFloors": 2,
        "PropertyGFAParking": 0,
        "PropertyGFABuildings": 25840,
        "ListOfAllPropertyUseTypes": "Non-Refrigerated Warehouse",
        "LargestPropertyUseType": "Non-Refrigerated Warehouse",
        "LargestPropertyUseTypeGFA": 25840.0,
        "ComplianceStatus": "Compliant"
    },
    "Exemple 3 : Payload Complet (Restaurant)": {
        "BuildingType": "NonResidential",
        "PrimaryPropertyType": "Restaurant",
        "Neighborhood": "Downtown",
        "YearBuilt": 1985,
        "NumberofBuildings": 1.0,
        "NumberofFloors": 2,
        "PropertyGFAParking": 18036,
        "PropertyGFABuildings": 32297,
        "ListOfAllPropertyUseTypes": "Office",
        "LargestPropertyUseType": "Office",
        "LargestPropertyUseTypeGFA": 50333,
        "SecondLargestPropertyUseType": None,
        "SecondLargestPropertyUseTypeGFA": None,
        "ThirdLargestPropertyUseType": None,
        "ThirdLargestPropertyUseTypeGFA": None,
        "ENERGYSTARScore": 50.0,
        "steam_use_kbtu": 0.0,            
        "electricity_kbtu": 358030.9,    
        "natural_gas_kbtu": 3748445,      
        "ComplianceStatus": "Compliant",
        "Outlier": None,
        "GHGEmissionsIntensity": 6.69
    },
}

with st.sidebar:
    st.header("Configuration")
    
    # Textbox pour modifier l'URL de l'API dynamiquement
    api_url = st.text_input(
        "URL de l'API / Route de prédiction :",
        value="https://projet-5-1.onrender.com/predict",
        help="Modifiez cette URL pour pointer vers votre environnement local (ex: http://localhost:8000/predict)"
    )
    
    st.info(f"Requêtes envoyées à :\n`{api_url}`")

st.title("Prédiction de consommation énergétique d'un bâtiment")
st.write("Sélectionnez un exemple, modifiez-le si nécessaire au format JSON, puis envoyez la requête à l'API.")

selected_sample_name = st.selectbox(
    "Choisir un jeu de données d'entrée :",
    options=list(SAMPLES.keys())
)

default_json = SAMPLES[selected_sample_name]

# On convertit le dict en chaîne formatée pour l'affichage
json_input_str = st.text_area(
    "Données d'entrée (JSON modifiable) :",
    value=json.dumps(default_json, indent=4, ensure_ascii=False),
    height=350
)

if st.button("Prédire la consommation", use_container_width=True):
    try:
        # Validation que le texte saisi est bien du JSON valide avant l'envoi
        payload = json.loads(json_input_str)
        
        with st.spinner("Appel de l'API en cours..."):            
            response = requests.post(
                api_url, 
                json=payload, 
                headers={"Content-Type": "application/json"}
            )
            
        st.subheader("Statut de la réponse")
        if response.status_code == 200:
            st.success(f"HTTP {response.status_code} - Succès")
            
            result = response.json()
            predictions = result.get("prediction", [])
            
            st.subheader("Résultat de la prédiction")
            if predictions:
                st.metric(label="Consommation énergétique prédite pour le bâtiment", value=f"{predictions[0]:,.2f} kBtu")
            else:
                st.warning("Aucune donnée de prédiction dans la réponse.")
                
        else:
            st.error(f"HTTP {response.status_code} - Erreur")
            st.json(response.json()) 

    except json.JSONDecodeError:
        st.error("Erreur de syntaxe JSON. Veuillez vérifier le format de vos données d'entrée.")
    except requests.exceptions.RequestException as e:
        st.error(f"Impossible de joindre l'API. Détails : {e}")