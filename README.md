<a id="readme-top"></a>

# Projet 5
Déployez un modèle de machine learning

## A propos du projet
Le projet a pour but de déployer un modèle de régression linéaire via le CI/CD (Continuous Integration et Continuous Deployment) et de l'exposer via une API.

Le développement a été effectué sur un système d'exploitation Windows.

Le projet comprend :
   - le modèle de prédiction de la consommation énergétique d'un bâtiment
   - une API qui va nous permettre d'interagir avec le modèle de prédiction
   - une base de données PostgreSQL pour logger les interactions entre l'utilisateur et l'API
   - une interface client de démonstration pour interagir avec l'API
   - les tests unitaires, d'intégration et fonctionnels du code

### Le modèle de prédiction
Le modèle a pour but de prédire la consommation énergétique normalisée d'un bâtiment, divisée par sa superficie brute. Il a été entraîné à partir des données de la ville de Seattle qui sont disponibles dans le fichier csv `/data/raw/building_consumption.csv`. La prédiction sera exprimée en `[kBtu/sf]`.

Il s'agit du modèle de machine learning [**Random forest regressor**][randomforest-url] disponible dans la librairie [*SciKit-learn*][sklearn-url].

#### Entraînement du modèle
L'entraînement du modèle de prédiction se fait via le script *src/model/train.py*.
Celui-ci se déroule en plusieurs étapes :
- La lecture des données d'entraînement : Initialement fait à partir de la lecture du fichier CSV */data/raw/building_consumption.csv*. Cette partie de code a été mise en commentaire pour récupérer des données d'entraînement à partir de la base de données PostgreSQL.
- Le nettoyage des données manquantes et valeurs aberrantes
- La suppression des features inutiles
- L'application du feature engineering
- La création du pipeline de prétraitement, ainsi que du modèle
- La séparation du jeu de données en deux : un jeu d'entraînement et un de test (80 % - 20%)
- L'entraînement du modèle sur le jeu d'entraînement
- L'évaluation du modèle sur le jeu de test
- L'enregistrement du pipeline de prétraitement et du modèle dans le fichier */data/model/pipeline_model.pkl* pour l'utilisation de celui-ci en production

**Remarque** : Les méthodes de nettoyage et de prétraitement des données sont définies dans le script */src/model/preprocessing.py* et sont également utilisées en production pour nettoyer les données lors d'une requête de prédiction.

**Note** : Les résultats de l'évaluation du modèle sur les données d'entraînement originales sont :
- R² Score: 0.545
- Mean Absolute Error: 8.195
- Mean Squared Error: 126.211

#### Modèle en production
En production, le modèle est exposé via une API à laquelle il est possible d'exécuter une requête `/predict`. l'exécution se déroule alors de la façon suivante :
- Validation des données envoyées dans la requête via la librairie [*Pydantic*][pydantic-url]
- Enregistrement des données d'entrées dans la base de données
- Nettoyage des données d'entrée via les méthodes de préprocessing (*/src/model/preprocessing.py*)
- Application du feature engineering sur les données
- Prédiction de la valeur de sortie (consommation énergétique du bâtiment)
- Enregistrement de la prédiction dans la base de données
- Réponse de la prédiction à l'utilisateur

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### API
Schéma d'architecture :
<img src="./images/schema architecture.png" alt="Endpoints API" width="400">

L'API expose le modèle de prédiction. Il y a au total deux endpoints :
<img src="./images/endpoints api.png" alt="Endpoints API" width="400">

Lors du déploiement de l'application dans l'environnement de développement, l'adresse de l'API est : 
<code>http://localhost:8000</code>

Pour accéder à l'application dans l'environnement de production, l'adresse de l'API est :
<code>https://projet-5-1.onrender.com</code>

Pour plus de détails sur les différents endpoints (schémas requis, codes erreurs, etc.), veuillez vous référer à la documentation OpenAPI générée pour l'API en ajoutant `/docs` à l'adresse URL ex : [`http://localhost:8000/docs`][local-api-url]

### Programmation

   * [Python V3.14][python-url]
   * [Package manager : uv][uv-url]
   * [Versionning : GIT][git-url]
   * [Base de données : PostgreSQL][postgresql-url]

### Plateformes

   * [VS Code][vscode-url]
   * [Docker desktop][docker-url]
   * [Github][github-url]
   * [Render][render-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Prérequis

   Avant de commencer le projet, veuillez préparer correctement votre environnement de développement.

      1. Installez Python version V3.14
      2. Installez Visual Studio Code, ainsi que ses extensions Python (python, python debugger, ...)
      3. Installez Docker desktop
      4. Installez le système de contrôle de version Git
      5. Installez le manager de packages et d'environnements UV

### Installation package manager UV

Ouvrez la console Powershell et tapez la commande suivante pour installer UV :

   ```sh
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

### Cloner le projet depuis le repo GitHub

Pour commencer à travailler en local sur le projet, veuillez cloner celui-ci avec la commande suivante (via GIT bash) :

   ```sh
   git clone https://github.com/clementghoris-cpu/Projet-5.git
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Organisation des branches
- La documentation se fait dans les branches `docs/*`
- Les fonctionnalités se font dans les branches `features/*`
- La branche principale de développement est `develop`. Elle récupère les mises à jours des fonctionnalités via les pull requests
- La branche `release` est utilisée pour le déploiement sur l'environnement *staging* pour exécuter les tests d'intégration et fonctionnels. Elle est mise à jour via un *pull request* de la branche develop vers celle-ci
- la branche `main` sert au déploiement sur l'environnement de *production*. Elle est mise à jour automatiquement après que les tests d'intégration et fonctionnels soient validés par un *merge* de la branche `release` vers `main` généré par le github action (déploiement continu)

### Convention pour les commits
La structure d'un message de commit se fait de la façon suivante :

```sh
   <type> (cible) : description

   Exemple : feat (api) : modifier le format de la reponse de l'endpoint /predict
```

#### Les principaux types
- **`feat`** : Nouvelle fonctionnalité
- **`fix`** : Correction d'un bug
- **`docs`** : Changement dans la documentation
- **`refactor`** : Modification du code qui ne corrige rien et n'ajoute rien
- **`test`** : Ajout ou modification de tests
- **`chore`** : Tâches répétitives, mise à jour de dépendances, configuration des outils

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Environnement de développement
Il y a trois environnements différents :
   - l'environnement de *développement* (en local), qui va nous permettre de tester l'application via des conteneurs Docker
   - l'environnement *staging*, qui a la même configuration que l'environnement de *production* et dans lequel le projet sera automatiquement déployé via une *Github Action*. Il va nous permettre d'exécuter les tests d'intégration et les tests fonctionnels.
   - L'environnement de *production* dans lequel le projet sera automatiquement déployé après avoir réussi l'ensemble des tests

Pour les environnements *staging* et de *production*, la plateforme Render sera utilisée.

### Déploiement sur l'environnement de développement
Le déploiement de l'application sur l'environnement de développement se fait dans les conteneurs Docker.
Nous avons au total 4 conteneurs qui peuvent être utilisés : 
   - **Trainer** : qui est utilisé pour l'entraînement du modèle de prédiction
   - **api** : qui est l'application permettant d'exposer le modèle
   - **db** : qui contient la base de données postgreSQL
   - **pgadmin** : qui permet l'administration de la base de données 

Les conteneurs sont configurés via le fichier Dockerfile pour l'API et les fichiers docker-compose.yml et docker-compose.test.yml.

Pour déployer les containers, utilisez la commande :
   ```sh
   docker compose -f docker-compose.yml -f docker-compose.test.yml up -d [api] [db] [pgadmin] [trainer] --build
   ```

Pour démarrer la totalité des conteneurs, il n'est pas utile de spécifier chaque nom de container. `--build` permet de recompiler les conteneurs après une modification de code.

#### Container "Trainer"
Le container Trainer va permettre d'entrainer le modèle et générer le pipeline de préprocessing + le modèle dans le fichier */data/model/pipeline_model.pk* via l'exécution du script *src/model/train.py*.

Le fichier généré est automatiquement intégré au dépôt et sera déployé dans les différents environnements.

Le démarrage du conteneur fait deux choses :
- Il exécute le script init_db.py afin d'initialiser la base de données et de l'alimenter avec les données utiles à l'entrainement du modèle
- Il exécute ensuite le script *src/model/train.py*

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## CI / CD (intégration continue / déploiement continu)
Le déploiement sur les environnements *staging* et *production* se fait via l'intégration continue / déploiement continu.

Les étapes du CI / CD se font de la façon suivante :
<img src="./images/etapes ci-cd.png" alt="Endpoints API" width="600">

1. Après un commit sur les branches `features/*`, `docs/*` ou encore `develop`, l'utilisateur fait un push vers le dépôt GitHub
2. Le workflow CI défini dans le fichier **.github/workflows/ci-features.yml** se déclenche automatiquement dans une action GitHub et déclenche les tests unitaires définis dans le dossier ***/tests/unit/***
3. Si les tests passent :
   1. Si les modifications viennent des branches `features/*`et `docs/*`, l'utilisateur *merge* d'abord vers la branche `develop`
   2. L'utilisateur crée une *pull request* pour fusionner le code de la branche `develop` vers la branche `release`
4. La fusion vers la branche `release` entraîne automatiquement l'exécution du workflow CD défini dans le fichier **.github/workflows/cd-staging+prod.yml** via une action Github et entraine :
   1. Le déploiement de l'application dans l'environnement *staging*
   2. L'exécution des tests d'intégration (***/tests/integration***) et fonctionnels (***/tests/functional***)
   3. Si les tests passent, la fusion de la branche `release` vers la branche `main` et la création d'une  *release* (Tag)
   4. Le déploiement vers l'environnement de *production*

### Fichier *ci-features.yml*
- Déclenchement sur un *push* de la branche `features/*`, `docs/*` ou `develop`
- Jobs :
   - analyse et tests :
      1. Récupération du dépôt (*checkout*)
      2. Installation de Python
      3. Installation du package manager UV
      4. Installation des dépendances
      5. Vérification de la qualité du code (Ruff)
      6. Exécution des tests unitaires

### Fichier *cd-staging+prod.yml*
- Déclenchement sur un *push* de la branche `release` (fait via une pull request de la branche `develop`)
- Jobs :
   - Déploiement en staging :
      1. Récupération du dépôt (*checkout*)
      2. Déclenchement du déploiement sur l'environnement staging de la plateforme Render
      3. Attendre que l'environnement sur Render soit opérationnel
      4. Installation de Python
      5. Installation du package manager UV
      6. Installation des dépendances
      7. Exécution des tests d'intégration et fonctionnels
   - Merge et release :
      1. Récupération du dépôt (*checkout*)
      2. Configuration de GIT (utilisateur [BOT])
      3. Fusion de la branche `release` dans `main`
      4. Génération automatique du tag de version
      5. Création et publication de la Release sur GitHub
   - Approbation pour la production :
      1. Création d'une ***issue*** pour demander l'approbation pour passer à l'étape de déploiement en production
   - Dépoiement en production :
      1. Déclenchement du déploiement sur l'environnement production de la plateforme Render
      2. Attendre que le déploiement sur la production soit terminé
       
<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Variables d'environnement et secrets
Pour protéger l'accès à la base de données et aux environnements, plusieurs variables d'environnement et secrets sont créées.

#### Fichier .env
Il est utilisé uniquement dans l'environnement de développement, pour configurer l'accès à la base de données et au service *pgAdmin* qui seront déployés dans Docker. Il est ignoré du dépôt et donc n'est pas transféré sur GitHub. Néanmoins, pour savoir comment ce fichier doit être rempli sur votre environnement, il y a un fichier d'exemple ***.env.example***.

#### Github secrets
Dans les paramètres du dépôt sur GitHub, deux environnements ont été créés pour y insérer les variables secrets :
- *staging* : reprend l'ensemble des secrets utiles au déploiement et aux tests sur l'environnement de staging
   1. **POSTGRES_DB** : Nom de la base de données
   2. **POSTGRES_HOST** : Nom de l'hôte où se trouve la base de données
   3. **POSTGRES_PASSWORD** : Mot de passe pour accéder à la base de données
   4. **POSTGRES_PORT** : Port de la base de données
   5. **POSTGRES_USER** : Nom d'utilisateur pour accéder à la base de données
   6. **RENDER_API_KEY** : Clé d'API Render (disponible dans les settings de la plateforme Render)
   7. **RENDER_SERVICE_ID** : Numéro de service web de l'environnement staging
   8. **RENDER_STAGING_DEPLOY_HOOK** : Adresse URL pour déclencher le déploiement de l'application sur le service web
   9. **STAGING_API_URL** : Adresse URL d'accès à l'API dans l'environnement de staging

   **Note** : Attention : bien spécifier les informations de la base de données pour un accès depuis l'extérieur de la plateforme *Render* car on accède à la base de données depuis l'action GitHub (GitHub runner)

- *production* : reprend l'ensemble des secrets utiles au déploiement sur l'environnement de production
   1. **RENDER_API_KEY** : Clé d'API Render (disponible dans les settings de la plateforme Render)
   2. **RENDER_PRODUCTION_DEPLOY_HOOK** : Adresse URL pour déclencher le déploiement de l'application sur le service web
   3. **RENDER_PRODUCTION_SERVICE_ID** : Numéro de service web de l'environnement production

**Remarques** : ces secrets sont référencés dans les fichier ***ci-features.yml*** et ***cd-staging+prod.yml***

#### Render secrets
Sur la plateforme *Render*, plusieurs secrets doivent être configurés pour que l'application (API) puisse accéder à la base de données tant sur l'environnement staging que sur l'environnement de production.
Ce sont les mêmes secrets pour les deux environnements mais ils doivent être configurés sur chacun d'eux.
Dans ***My Workspace > Staging (ou production) > Environnement > Environnement Variables*** ajoutez les secrets suivants : 
1. **POSTGRES_DB** : Nom de la base de données
2. **POSTGRES_HOST** : Nom de l'hôte où se trouve la base de données
3. **POSTGRES_PASSWORD** : Mot de passe pour accéder à la base de données 
4. **POSTGRES_PORT** : Port de la base de données
5. **POSTGRES_USER** : Nom d'utilisateur pour accéder à la base de données

**Note** : Pour ces secrets, étant donnée que la base de données est également hébergé sur la plateforme Render, il est possible de renseigner les informations pour l'accès intra-services (*informations disponibles dans les Settings de la base de données*). 


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Tests et rapport de couverture
Il existe 3 types de tests pour le projet :
- Les tests unitaires : on isole chaque méthode et on vérifie son comportement pour différentes entrées
- Les tests d'intégration : on teste le bon fonctionnement conjoint de plusieurs composants système
- Les tests fonctionnels : on valide l'application du point de vue de l'utilisateur final

Ils ont été programmé avec la librairie [Pytest][pytest-url].

Pour l'environnement de développement, il est possible de lancer les tests avec la commande suivante :
```sh
   uv run pytest .\tests\[unit\][integration\]
```

Sinon, ils sont exécutés automatiquement via le CI / CD. Les tests unitaires sont exécutés dans le CI lorsqu'on fait un push vers GitHub. Les tetss d'intégration et fonctionnels sont sont exécutés dans le CD lors du déploiement sur l'environnement Staging.

Le rapport de couverture permet de mesurer la quantité de code couvert par les tests. 
Pour permettre de récupérer le rapport de test, il faut tapez les commandes suivantes :
```sh
   coverage run -m pytest tests/unit/
   # Une fois le test terminé
   coverage report -m
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Base de données
La base de données est utilisée pour deux raisons :
- Stocker les données d'entraînement
- Logger les interactions entre l'API (données d'entrée de la requête) et le modèle (résultat de la prédiction)

Nous avons 3 tables :
- une table `TrainData` : pour stocker les données d'entraînement
- une table `PredictionInput` : pour logger les données d'entrée
- une table `PredictionOutput` : pour logger les résultats des prédictions

 <img src="./images/uml base de donnees postgres.png" alt="Description" width="900">

L'interface d'accès à la base de données est programmée dans le script `src/database/db_manager.py`. Pour le *mapping* des modèles, les classes ont été définies dans le script `src/database/models.py`.

L'initialisation du *mapping* des tables et l'alimentation des données d'entraînement dans la base de données se fait par via le script 'src/database/init_db.py`. Dans l'environnement de *développement*, le script s'exécute au démarrage du conteneur **Trainer**. Autrement, il s'exécute lors de l'exécution du script shell **entrypoint** qui est appelé à la fin du Dockerfile.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Interface démo
Une interface client a été créée à des fins de démonstration pour montrer le fonctionnement d'un appel à *l'endpoint* `/predict`. Le script a été créé avec [streamlit][streamlit-url] dans le fichier ***src/client/client.py***.

Pour démarrer cette interface client, tapez la commande suivante :
   ```sh
    streamlit run .\src\client\client.py
   ```

une page web s'ouvre alors automtiquement sur l'interface client. Si ce n'est pas le cas, rendez-vous à l'adresse <code>http://localhost:8501</code>. L'interface vous permet de sélectionner plusieurs exemples de données et d'exécuter une requête vers l'API. Celle-ci retournera la prédiction en réponse.




[randomforest-url]:https://scikit-learn.org/stable/modules/ensemble.html
[sklearn-url]:https://scikit-learn.org/stable/index.html
[pydantic-url]:https://pydantic.dev/docs/
[local-api-url]:http://localhost:8000/docs
[python-url]:https://www.python.org/
[uv-url]:https://docs.astral.sh/uv/
[git-url]:https://git-scm.com/
[postgresql-url]:https://www.postgresql.org/
[vscode-url]:https://code.visualstudio.com/download?_exp_download=fb315fc982
[docker-url]:https://www.docker.com/products/docker-desktop/
[github-url]:https://github.com/
[render-url]:https://render.com/
[streamlit-url]:https://streamlit.io/
[pytest-url]:https://docs.pytest.org/en/stable/