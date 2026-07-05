import sys
import os
import psycopg2
from dotenv import load_dotenv

# Vérifie si l'application s'exécute dans un environnement compilé par PyInstaller
# Cela permet de savoir si on est en mode développement ou en mode exécutable
if getattr(sys, 'frozen', False):
    # En cours d'exécution en tant qu'exécutable compilé : cherche le fichier .env dans le même dossier que l'exécutable
    dotenv_path = os.path.join(os.path.dirname(sys.executable), '.env')
else:
    # En cours d'exécution en mode développement : cherche le fichier .env dans le dossier racine du projet
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')

# Charge les paramètres de connexion depuis le fichier .env identifié
load_dotenv(dotenv_path)

def get_connection():
    """
    Crée et retourne une nouvelle connexion à la base de données PostgreSQL.
    Lit les identifiants directement à partir des variables d'environnement.
    """
    # Établit la connexion en utilisant les informations de la base de données
    return psycopg2.connect(
        host=os.getenv("DB_HOST"), # L'adresse de la base de données
        port=os.getenv("DB_PORT"), # Le port de connexion
        dbname=os.getenv("DB_NAME"), # Le nom de la base de données
        user=os.getenv("DB_USER"), # Le nom d'utilisateur pour se connecter
        password=os.getenv("DB_PASSWORD") # Le mot de passe de connexion
    )
