# Projet-5
Déployez un modèle de Machine Learning

## A propos du projet
Le projet a pour but de déployer un modèle de régression linéaire via le CI/CD (Continuous Integration et Continuous Deployment) et de l'exposer via une API.

- mise en place de l'environnement de développement (uv)
- expliquer la mise en place de uv pre-commit pour générer automatiquement le fichier requirements.txt utile au déploiement

- schéma requête predict

    {
    "BuildingType": "string",
    "PrimaryPropertyType": "string",
    "Neighborhood": "string",
    "YearBuilt": 0,
    "NumberofBuildings": 0,
    "NumberofFloors": 0,
    "PropertyGFAParking": 0,
    "PropertyGFABuilding(s)": 0,
    "ListOfAllPropertyUseTypes": "string",
    "LargestPropertyUseType": "string",
    "LargestPropertyUseTypeGFA": 0,
    "SecondLargestPropertyUseType": "string",
    "SecondLargestPropertyUseTypeGFA": 0,
    "ThirdLargestPropertyUseType": "string",
    "ThirdLargestPropertyUseTypeGFA": 0,
    "ENERGYSTARScore": 0,
    "SteamUse(kBtu)": 0,
    "Electricity(kBtu)": 0,
    "NaturalGas(kBtu)": 0,
    "ComplianceStatus": "string",
    "Outlier": "string",
    "GHGEmissionsIntensity": 0
    }

- parler du container "trainer" à démarrer pour entrainer le modèle

- parler des étapes CI/CD 
    feature/mon-code
       │  (PR + Tests Unitaires)
       ▼
    develop     ──► [Environnement de Dev local / Sandbox]
       │  
       ▼  (Merge pour préparer la version)
    release     ──► Déploiement en STAGING ──► Exécution Tests Intégration & E2E
       │  
       ▼  (Si Vert : Merge + Tag vX.Y.Z)
     main       ──► Déploiement en PRODUCTION

   - expliquer comment créer les secrets dans Render ainsi que dans github (pour environnement staging et production)