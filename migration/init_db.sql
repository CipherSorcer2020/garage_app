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

-- TECHNICIENS
-- Un technicien peut etre responsable de plusieurs vehicules.
CREATE TABLE techniciens (
    id            SERIAL PRIMARY KEY,
    nom           VARCHAR(100) NOT NULL,
    prenom        VARCHAR(100) NOT NULL DEFAULT '',
    qualification VARCHAR(150) NOT NULL DEFAULT '',
    telephone     VARCHAR(30)  NOT NULL DEFAULT '',
    cout_horaire  NUMERIC(10,2) DEFAULT 0.0
);

-- VEHICULES
-- Chaque vehicule appartient a un client et peut avoir un technicien responsable.
CREATE TABLE vehicules (
    id             SERIAL PRIMARY KEY,
    client_id      INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    immatriculation VARCHAR(20) UNIQUE NOT NULL,
    vin            VARCHAR(50),
    marque         VARCHAR(100),
    modele         VARCHAR(100),
    annee          INTEGER,
    kilometrage    INTEGER,
    technicien_id  INTEGER REFERENCES techniciens(id) ON DELETE SET NULL
);

-- ORDRES DE REPARATION
CREATE TABLE ordres_reparation (
    id SERIAL PRIMARY KEY,
    vehicule_id INTEGER REFERENCES vehicules(id),
    mecanicien_id INTEGER REFERENCES utilisateurs(id),
    statut VARCHAR(50) DEFAULT 'reception',
    date_entree DATE DEFAULT CURRENT_DATE,
    date_sortie DATE,
    description TEXT,
    kilometrage INTEGER,
    niveau_carburant VARCHAR(50),
    visual_condition TEXT,
    accessoires TEXT,
    signature BYTEA
);

-- DIAGNOSTICS
CREATE TABLE diagnostics (
    id SERIAL PRIMARY KEY,
    or_id INTEGER REFERENCES ordres_reparation(id) ON DELETE CASCADE,
    observations TEXT,
    date_diagnostic DATE DEFAULT CURRENT_DATE
);

-- PHOTOS (avant/pendant/après intervention)
CREATE TABLE or_photos (
    id SERIAL PRIMARY KEY,
    or_id INTEGER REFERENCES ordres_reparation(id) ON DELETE CASCADE,
    description VARCHAR(255),
    image_data BYTEA NOT NULL,
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

-- FOURNISSEURS
CREATE TABLE fournisseurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    contact VARCHAR(100),
    telephone VARCHAR(30),
    email VARCHAR(150),
    adresse TEXT
);

-- COMMANDES FOURNISSEURS
CREATE TABLE commandes_fournisseurs (
    id SERIAL PRIMARY KEY,
    fournisseur_id INTEGER REFERENCES fournisseurs(id) ON DELETE RESTRICT,
    statut VARCHAR(50) DEFAULT 'brouillon',
    date_commande DATE DEFAULT CURRENT_DATE,
    date_reception DATE
);

-- PIECES (stock de pieces detachees)
CREATE TABLE pieces (
    id            SERIAL PRIMARY KEY,
    reference     VARCHAR(100),
    designation   VARCHAR(255) NOT NULL,
    quantite      INTEGER      NOT NULL DEFAULT 0,
    prix_unitaire NUMERIC(10,2),
    emplacement   VARCHAR(100),
    fournisseur_id INTEGER REFERENCES fournisseurs(id) ON DELETE SET NULL
);

-- LIGNES COMMANDE FOURNISSEUR
CREATE TABLE lignes_commande_fournisseur (
    id SERIAL PRIMARY KEY,
    commande_id INTEGER REFERENCES commandes_fournisseurs(id) ON DELETE CASCADE,
    piece_id INTEGER REFERENCES pieces(id) ON DELETE RESTRICT,
    quantite_commandee INTEGER NOT NULL DEFAULT 1,
    quantite_recue INTEGER NOT NULL DEFAULT 0,
    prix_achat_unitaire NUMERIC(10,2) NOT NULL
);

-- RETOURS DE PIECES (retour fournisseur ou garantie)
CREATE TABLE retours_piece (
    id SERIAL PRIMARY KEY,
    piece_id INTEGER REFERENCES pieces(id) ON DELETE RESTRICT,
    quantite INTEGER NOT NULL DEFAULT 1,
    motif TEXT,
    date_retour DATE DEFAULT CURRENT_DATE,
    fournisseur_id INTEGER REFERENCES fournisseurs(id) ON DELETE SET NULL
);

-- ==========================================
-- PHASE 3 : CRM ET RELATION CLIENT
-- ==========================================

-- NOTIFICATIONS & RAPPELS
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    type_notification VARCHAR(50), -- 'rappel_revision', 'vehicule_pret', 'devis_attente'
    canal VARCHAR(20), -- 'email', 'sms', 'whatsapp'
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_envoi TIMESTAMP,
    statut VARCHAR(20) DEFAULT 'en_attente',
    message TEXT
);

-- RENDEZ-VOUS (Agenda Atelier)
CREATE TABLE rendez_vous (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    vehicule_id INTEGER REFERENCES vehicules(id) ON DELETE CASCADE,
    date_heure_prevue TIMESTAMP NOT NULL,
    duree_estimee_minutes INTEGER,
    statut VARCHAR(50) DEFAULT 'planifie', -- 'planifie', 'honore', 'annule', 'no_show'
    description TEXT
);

-- DOSSIERS SINISTRES (Assurances)
CREATE TABLE dossiers_sinistres (
    id SERIAL PRIMARY KEY,
    or_id INTEGER REFERENCES ordres_reparation(id) ON DELETE CASCADE,
    nom_assurance VARCHAR(100) NOT NULL,
    numero_dossier VARCHAR(100) NOT NULL,
    statut VARCHAR(50) DEFAULT 'ouvert', -- 'ouvert', 'expertise_en_cours', 'cloture', 'paye'
    montant_couvert NUMERIC(10,2) DEFAULT 0.0,
    date_creation DATE DEFAULT CURRENT_DATE
);

-- ==========================================
-- PHASE 4 : PILOTAGE ET ENTERPRISE
-- ==========================================

-- JOURNAL D'AUDIT (Traçabilité)
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    utilisateur_id INTEGER REFERENCES utilisateurs(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE'
    table_cible VARCHAR(50) NOT NULL,
    enregistrement_id INTEGER,
    date_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- CATALOGUE TEMPS BAREMES (Autodata / IA)
CREATE TABLE catalogue_temps_baremes (
    id SERIAL PRIMARY KEY,
    marque VARCHAR(100),
    modele VARCHAR(100),
    operation VARCHAR(255) NOT NULL,
    temps_heures NUMERIC(5,2) NOT NULL
);