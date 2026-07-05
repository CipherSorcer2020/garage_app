# Garage App — Système de Gestion d'Atelier Automobile

Application desktop de gestion d'atelier pour garage automobile, développée en Python avec PyQt6 et PostgreSQL.

---

## Fonctionnalités

- **Gestion des clients** — ajout, modification, suppression, recherche
- **Gestion des véhicules** — liés aux clients, validation de l'immatriculation marocaine
- **Ordres de Réparation (OR)** — workflow complet en 9 étapes
- **Devis** — saisie libre des pièces et main d'œuvre, calcul automatique HT/TTC
- **Facturation** — génération automatique, encaissement, export PDF
- **Tableau de bord** — indicateurs clés en temps réel

### Workflow OR
```
Réception → Diagnostic → Devis → Accord devis → Affectation mécanicien
         → En cours → Test → Facturé → Livré
```

---

## Stack technique

| Composant     | Technologie         |
|---------------|---------------------|
| Interface     | PyQt6               |
| Base de données | PostgreSQL        |
| Connecteur BDD | psycopg2-binary   |
| PDF           | ReportLab           |
| Config        | python-dotenv       |

---

## Prérequis

- Python 3.11+
- PostgreSQL 15+ installé et en cours d'exécution
- pip

---

## Installation

### 1. Cloner le projet

```bash
git clone https://github.com/TON_USERNAME/garage_app.git
cd garage_app
```

### 2. Installer les dépendances Python

```bash
pip install pyqt6 psycopg2-binary python-dotenv reportlab
```

### 3. Configurer la base de données

Créer la base dans PostgreSQL (via pgAdmin ou terminal) :

```sql
CREATE DATABASE garage_db
    WITH ENCODING 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252';
```

Puis exécuter le script de création des tables :

```bash
psql -U postgres -d garage_db -f migrations/sql_querry.sql
```

Ou ouvrir `migrations/sql_querry.sql` dans pgAdmin et l'exécuter manuellement.

### 4. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=garage_db
DB_USER=postgres
DB_PASSWORD=ton_mot_de_passe
```

### 5. Lancer l'application

```bash
cd garage_app
python main.py
```

---

## Structure du projet

```
garage_app/
│
├── main.py                        # Point d'entrée de l'application
├── .env                           # Variables d'environnement (non versionné)
├── requirements.txt               # Dépendances Python
│
├── config/
│   └── database.py                # Connexion PostgreSQL via psycopg2
│
├── models/                        # Classes de données (dataclasses)
│   ├── client.py
│   ├── vehicule.py
│   ├── ordre_reparation.py
│   ├── diagnostic.py
│   ├── devis.py
│   ├── ligne_piece.py
│   ├── ligne_main_oeuvre.py
│   ├── facture.py
│   └── utilisateur.py
│
├── repositories/                  # Accès aux données (requêtes SQL)
│   ├── client_repo.py
│   ├── vehicule_repo.py
│   ├── or_repo.py
│   ├── diagnostic_repo.py
│   ├── devis_repo.py
│   ├── ligne_piece_repo.py
│   ├── ligne_mo_repo.py
│   ├── facture_repo.py
│   └── utilisateur_repo.py
│
├── services/                      # Logique métier
│   ├── or_service.py              # Workflow OR, devis, affectation
│   ├── facturation_service.py     # Génération et encaissement factures
│   └── pdf_service.py             # Export PDF (factures et devis)
│
├── ui/                            # Interface PyQt6
│   ├── windows/
│   │   └── main_window.py         # Fenêtre principale + navigation
│   ├── widgets/
│   │   ├── dashboard_widget.py    # Tableau de bord
│   │   ├── client_widget.py       # Page clients
│   │   ├── vehicule_widget.py     # Page véhicules
│   │   ├── or_widget.py           # Page ordres de réparation
│   │   └── facture_widget.py      # Page facturation
│   ├── dialogs/
│   │   ├── client_dialog.py       # Formulaire client
│   │   ├── vehicule_dialog.py     # Formulaire véhicule
│   │   ├── or_dialog.py           # Formulaire nouvel OR
│   │   └── or_detail_dialog.py    # Détail OR (diagnostic, devis, affectation)
│   └── styles/
│       └── theme.qss              # Thème sombre (palette industrielle)
│
├── migrations/
│   └── sql_querry.sql             # Script de création des tables PostgreSQL
│
└── output/                        # PDF générés (créé automatiquement)
```

---

## Utilisation

### Créer un premier dossier complet

1. **Clients** → cliquer `+ Nouveau client` → remplir le formulaire
2. **Véhicules** → cliquer `+ Nouveau véhicule` → choisir le client → saisir l'immatriculation (format : `12345-A-5`)
3. **Ordres de réparation** → cliquer `+ Nouvel OR` → choisir le véhicule
4. **Ouvrir l'OR** → double-clic ou bouton `Ouvrir / Avancer`
   - Onglet **Diagnostic** → saisir les observations → `Enregistrer diagnostic`
   - Onglet **Devis & Pièces** → ajouter les pièces et la main d'œuvre → `Enregistrer le devis`
   - Cliquer `Accepter devis` si le client valide
   - Onglet **Affectation** → choisir un mécanicien → `Affecter`
   - Bouton `▶ Avancer le statut` pour progresser dans le workflow
   - Bouton `Générer facture` quand le travail est terminé
5. **Facturation** → sélectionner la facture → `Marquer payée` → choisir le mode → `Générer PDF`

### Format immatriculation

Le système accepte uniquement le format marocain :

```
NNNNN-L-RR
```
- `NNNNN` : numéro de 1 à 99999
- `L` : une lettre (série)
- `RR` : région de 1 à 88

Exemples valides : `12345-A-5`, `100-B-22`, `1-A-1`, `99999-Z-88`

### PDF générés

Les PDF sont sauvegardés dans le dossier `output/` à la racine du projet :
- Factures : `output/F-2025-0001.pdf`
- Devis : `output/DEVIS-OR1.pdf`

---

## Variables d'environnement

| Variable      | Description               | Valeur par défaut |
|---------------|---------------------------|-------------------|
| `DB_HOST`     | Hôte PostgreSQL           | `localhost`       |
| `DB_PORT`     | Port PostgreSQL           | `5432`            |
| `DB_NAME`     | Nom de la base            | `garage_db`       |
| `DB_USER`     | Utilisateur PostgreSQL    | `postgres`        |
| `DB_PASSWORD` | Mot de passe              | *(obligatoire)*   |

---

## Données de test

Pour peupler la base avec des données de démonstration :

```bash
psql -U postgres -d garage_db -f migrations/seed_data.sql
```

---

## Licence

Projet de stage — Usage interne.
