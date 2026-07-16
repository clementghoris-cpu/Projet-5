<a id="readme-top"></a>

# Projet 5
Déployez un modèle de Machine Learning

## A propos du projet
Le projet a pour but de déployer un modèle de régression linéaire via le CI/CD (Continuous Integration et Continuous Deployment) et de l'exposer via une API.

Le développement a été effectuée sur un système d'exploitation Windows.

### Programmation

   * [Python V3.14][python-url]
   * [package manager : uv][uv-url]
   * [versionnning : GIT][git-url]
   * [base de données : PostgreSQL][postgresql-url]

### Plateformes

   * [VS Code][vscode-url]
   * [Docker desktop][docker-url]
   * [Github][github-url]
   * [Render][render-url]

## Prérequis

   Avant de commencer le projet, veuillez préparer correctement votre environnement de développement.

      1. Installez python version V3.14
      2. Installez visual studio code, ainsi que ses extensions python (python, python debugger, ...)
      3. Installez docker desktop
      4. Installez le système de contrôle de version GIT
      5. Installez le manager de packages et d'environnements UV

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Installation package manager UV

Ouvrez la console Powershell et tapez la commande suivante pour installer UV :

   <code>powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"</code>













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

   - parler de la surcharge du docker commande paramétré dans Render settings

   - démarrer le client : streamlit run .\src\client\client.py

      ![UML base de données](./images/uml%20base%20de%20donnees%20postgres.png) ou <img src="./images/capture.png" alt="Description" width="400"> (si on souhaite redimenssioner l'image)




      [python-url]:https://www.python.org/
      [uv-url]:https://docs.astral.sh/uv/
      [git-url]:https://git-scm.com/
      [postgresql-url]:https://www.postgresql.org/
      [vscode-url]:https://code.visualstudio.com/download?_exp_download=fb315fc982
      [docker-url]:https://www.docker.com/products/docker-desktop/
      [github-url]:https://github.com/
      [render-url]:https://render.com/