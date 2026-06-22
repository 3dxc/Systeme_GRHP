Système de Gestion des Ressources Humaines et de la Paie (SGRHP)

Ce projet est une application web complète dédiée à la gestion automatisée des ressources humaines et au traitement de la paie. Développé avec **Django** et **SQL Server**, il propose une interface moderne, sobre et épurée (bords arrondis, design moderne) pour optimiser les processus RH.

1.Guide d'Initialisation de Django et prérequis

Si vous repartez de zéro ou si vous configurez le projet pour la première fois, suivez ces étapes.
Assurez-vous d'avoir Python installé. Une fois fait, créez et activez un environnement virtuel pour isoler les dépendances :

---bash---
# Création de l'environnement virtuel
python -m venv venv

# Activation (Windows)
.\venv\Scripts\activate

# Activation (Linux/Mac)
source venv/bin/activate


2. Installation de Django et des Dépendances

pip install django mssql-django pyodbc
# Ou si un fichier requirements.txt est présent :
pip install -r requirements.txt


3. Création et Initialisation du Projet

# Créer le projet global
django-admin startproject sgrhp_project .

# Créer l'application dédiée au SGRHP
python manage.py startapp core


4.Configuration Spécifique du SGRHP (le Settings en python)

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('DB_NAME'),  # Récupère "systeme_GRHP" depuis le .env
        'USER': os.getenv('DB_USER'),
        'PASSWORD': '',
        'HOST': os.getenv('DB_HOST'),  # Récupère "localhost\SQLEXPRESS" depuis le .env
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            'extra_params': 'Trusted_Connection=yes;TrustServerCertificate=yes;',
        },
    }
}


5.Migrations et Lancement

# Générer les fichiers de migration
python manage.py makemigrations

# Appliquer les modifications sur SQL Server
python manage.py migrate

# Lancer le serveur local
python manage.py runserver


6.Fonctionnalités Principales du SGRHP

Le projet est articulé autour de modules clés gérés par notre logique de contrôleurs et nos routes dédiées :

 Gestion des Employés : Dossier numérique complet, suivi des contrats, postes et départements.

 Module de Paie : Calcul automatisé des salaires, primes, retenues et génération des bulletins de paie.

 Tableau de Bord Épuré : Interface utilisateur moderne avec un design sobre et des composants arrondis pour un confort visuel optimal.

 Architecture Robuste : Gestion stricte des relations de tables et intégrité des données financières et administratives.


7.Structure du Projet

├── sgrhp_project/          # Configuration globale de l'application
│   ├── settings.py         # Paramètres, configuration SQL Server et applications
│   └── urls.py             # Routage principal
├── core/                   # Application principale SGRHP
│   ├── models.py           # Modèles de données (Employés, Contrats, Bulletins de paie)
│   ├── views.py            # Logique des contrôleurs RH
│   ├── urls.py             # Routes spécifiques du module core
│   └── templates/          # Interfaces HTML & Styles CSS modernes
├── manage.py               # Script d'exécution Django
└── requirements.txt        # Liste des dépendances du projet
