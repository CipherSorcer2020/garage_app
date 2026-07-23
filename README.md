# Garage App — Système de Gestion d'Atelier Automobile

Application desktop de gestion d'atelier pour garage automobile, développée en Python avec PyQt6 et PostgreSQL.
Ce projet couvre 4 phases complètes, allant de la gestion basique d'atelier jusqu'au pilotage d'entreprise et CRM.

---

## Fonctionnalités

- **Gestion des clients et véhicules** — Fiches clients détaillées, validation d'immatriculation marocaine.
- **Workflow Ordres de Réparation (OR)** — 9 étapes clés : de la réception du véhicule à la facturation.
- **Devis et Facturation** — Saisie libre des pièces et main d'œuvre, calcul automatique HT/TTC, génération et export PDF.
- **Achats et Stocks (Fournisseurs)** — Création de commandes, réception et mise en stock, gestion des retours et garanties pièces.
- **CRM et Agenda** — Suivi des notifications clients (SMS/Email), gestion des rendez-vous et planification.
- **Assurances** — Gestion des dossiers sinistres liés aux ordres de réparation.
- **Audit et Traçabilité** — Journalisation complète de toutes les actions (création, modification, suppression).
- **Tableau de bord** — Indicateurs clés de performance en temps réel.

### Workflow OR
```text
Réception → Diagnostic → Devis → Accord devis → Affectation mécanicien
         → En cours → Test → Facturé → Livré
```

---

## Stack technique

| Composant       | Technologie         |
|-----------------|---------------------|
| Interface       | PyQt6               |
| Base de données | PostgreSQL          |
| Connecteur BDD  | psycopg2-binary     |
| PDF             | ReportLab           |
| Config          | python-dotenv       |
| CI/CD           | GitHub Actions      |

---

## Prérequis

- Python 3.11+
- PostgreSQL 15+ installé et en cours d'exécution
- pip

---

## Installation

### 1. Cloner le projet

```bash
git clone https://github.com/VOTRE_USERNAME/garage_app.git
cd garage_app
```

### 2. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 3. Configurer la base de données

Créer la base dans PostgreSQL (via pgAdmin ou terminal) :

```sql
CREATE DATABASE garage_db
    WITH ENCODING 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252';
```

Puis exécuter le script complet de création des tables :

```bash
psql -U postgres -d garage_db -f migration/init_db.sql
```

### 4. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=garage_db
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
```

### 5. Lancer l'application

```bash
python main.py
```

---

## Structure du projet

```text
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
│   ├── client.py, vehicule.py
│   ├── ordre_reparation.py, diagnostic.py, devis.py, facture.py
│   ├── ligne_piece.py, ligne_main_oeuvre.py
│   ├── technicien.py, utilisateur.py
│   ├── fournisseur.py, commande_fournisseur.py, piece.py
│   ├── retour_piece.py
│   ├── notification.py, rendez_vous.py, dossier_sinistre.py
│   └── audit_log.py
│
├── repositories/                  # Accès aux données (requêtes SQL)
│   ├── client_repo.py, vehicule_repo.py, or_repo.py
│   ├── diagnostic_repo.py, devis_repo.py, facture_repo.py
│   ├── technicien_repo.py, utilisateur_repo.py
│   ├── fournisseur_repo.py, commande_fournisseur_repo.py, piece_repo.py
│   ├── retour_piece_repo.py
│   ├── notification_repo.py, rendez_vous_repo.py, dossier_sinistre_repo.py
│   └── audit_log_repo.py
│
├── services/                      # Logique métier et orchestrations
│   ├── or_service.py              # Workflow OR complet
│   ├── facturation_service.py     # Gestion des factures
│   ├── pdf_service.py             # Création PDF
│   ├── commande_fournisseur_service.py
│   ├── retour_piece_service.py
│   └── audit_log_service.py
│
├── ui/                            # Interface Utilisateur PyQt6
│   ├── windows/
│   │   └── main_window.py         # Fenêtre principale et navigation
│   ├── widgets/                   # Vues des pages (Tableau de bord, Clients, etc.)
│   ├── dialogs/                   # Formulaires modaux (Nouvel OR, Nouveau client, etc.)
│   └── styles/
│       └── theme.qss              # Thème esthétique (Dark Mode Premium)
│
├── migration/
│   └── init_db.sql                # Script SQL unique pour créer toutes les tables
│
├── tests/                         # Tests unitaires
│   └── test_retour_piece_repo.py
│
├── .github/workflows/             # Intégration continue (CI)
│   └── ci.yml
│
└── output/                        # PDF générés
```

---

## Utilisation Courante

### Créer un premier dossier complet

1. **Clients** → Cliquer `+ Nouveau client` → Remplir le formulaire.
2. **Véhicules** → Cliquer `+ Nouveau véhicule` → Choisir le client → Saisir l'immatriculation.
3. **Ordres de réparation** → Cliquer `+ Nouvel OR` → Choisir le véhicule.
4. **Ouvrir l'OR** → Double-clic sur l'enregistrement.
   - Onglet **Diagnostic** → Saisir les observations.
   - Onglet **Devis & Pièces** → Ajouter les pièces et la main-d'œuvre.
   - Cliquer **Accepter devis** une fois validé.
   - Bouton **▶ Avancer le statut** pour progresser jusqu'à la facturation.
5. **Facturation** → Sélectionner la facture → **Marquer payée** → **Générer PDF**.

### Format immatriculation

Le système valide nativement le format marocain :
```text
NNNNN-L-RR
```
- `NNNNN` : numéro de 1 à 99999
- `L` : une lettre (série)
- `RR` : région de 1 à 88
*(Exemple valide : `12345-A-5`)*

---

## Licence

Projet développé dans le cadre d'un stage — Usage interne.
