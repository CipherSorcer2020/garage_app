-- UTILISATEURS
CREATE TABLE utilisateurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    login VARCHAR(50) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user'
);

-- CLIENTS
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100),
    telephone VARCHAR(20),
    email VARCHAR(150),
    adresse TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- VEHICULES
CREATE TABLE vehicules (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    immatriculation VARCHAR(20) UNIQUE NOT NULL,
    vin VARCHAR(50),
    marque VARCHAR(100),
    modele VARCHAR(100),
    annee INTEGER,
    kilometrage INTEGER
);

-- ORDRES DE REPARATION
CREATE TABLE ordres_reparation (
    id SERIAL PRIMARY KEY,
    vehicule_id INTEGER REFERENCES vehicules(id),
    mecanicien_id INTEGER REFERENCES utilisateurs(id),
    statut VARCHAR(50) DEFAULT 'reception',
    date_entree DATE DEFAULT CURRENT_DATE,
    date_sortie DATE,
    description TEXT
);

-- DIAGNOSTICS
CREATE TABLE diagnostics (
    id SERIAL PRIMARY KEY,
    or_id INTEGER REFERENCES ordres_reparation(id) ON DELETE CASCADE,
    observations TEXT,
    date_diagnostic DATE DEFAULT CURRENT_DATE
);

-- DEVIS
CREATE TABLE devis (
    id SERIAL PRIMARY KEY,
    or_id INTEGER REFERENCES ordres_reparation(id) ON DELETE CASCADE,
    montant_ht NUMERIC(10,2),
    tva NUMERIC(5,2) DEFAULT 20.00,
    statut VARCHAR(50) DEFAULT 'en_attente',
    date_creation DATE DEFAULT CURRENT_DATE,
    accepte BOOLEAN DEFAULT FALSE
);

-- LIGNES PIECES (saisie libre)
CREATE TABLE lignes_pieces (
    id SERIAL PRIMARY KEY,
    or_id INTEGER REFERENCES ordres_reparation(id) ON DELETE CASCADE,
    reference VARCHAR(100),
    designation VARCHAR(255) NOT NULL,
    quantite INTEGER DEFAULT 1,
    prix_unitaire_ht NUMERIC(10,2)
);

-- LIGNES MAIN D'OEUVRE
CREATE TABLE lignes_main_oeuvre (
    id SERIAL PRIMARY KEY,
    or_id INTEGER REFERENCES ordres_reparation(id) ON DELETE CASCADE,
    description VARCHAR(255) NOT NULL,
    duree_heures NUMERIC(5,2),
    taux_horaire_ht NUMERIC(10,2)
);

-- FACTURES
CREATE TABLE factures (
    id SERIAL PRIMARY KEY,
    or_id INTEGER REFERENCES ordres_reparation(id),
    client_id INTEGER REFERENCES clients(id),
    numero VARCHAR(50) UNIQUE NOT NULL,
    montant_ht NUMERIC(10,2),
    tva NUMERIC(5,2) DEFAULT 20.00,
    montant_ttc NUMERIC(10,2),
    statut VARCHAR(50) DEFAULT 'non_payee',
    date_emission DATE DEFAULT CURRENT_DATE,
    mode_paiement VARCHAR(50)
);