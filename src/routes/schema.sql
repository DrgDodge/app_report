-- schema.sql

-- Tabelul principal pentru clienti (pentru autocomplete)
CREATE TABLE IF NOT EXISTS Clienti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nume TEXT NOT NULL UNIQUE,
    cui TEXT,
    nr_reg_com TEXT,
    iban TEXT,
    adresa TEXT,
    locatie TEXT
);

-- Tabelul "master" pentru piese (pentru autocomplete)
CREATE TABLE IF NOT EXISTS PieseMaster (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pn TEXT NOT NULL UNIQUE,  -- Part Number
    descriere TEXT
);

CREATE TABLE IF NOT EXISTS Utilaje (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    nume TEXT NOT NULL,
    serie TEXT,
    FOREIGN KEY (client_id) REFERENCES Clienti(id)
);

CREATE TABLE IF NOT EXISTS OreFunctHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilaj_id INTEGER NOT NULL,
    ore_funct INTEGER NOT NULL,
    data TEXT NOT NULL,
    raport_id INTEGER,
    FOREIGN KEY (utilaj_id) REFERENCES Utilaje(id),
    FOREIGN KEY (raport_id) REFERENCES Rapoarte(id)
);

-- Tabelul central care tine raportul
CREATE TABLE IF NOT EXISTS Rapoarte (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numar_raport TEXT,
    tehnician TEXT,
    data TEXT NOT NULL,
    este_revizie INTEGER DEFAULT 0,
    este_reparatie INTEGER DEFAULT 0,
    este_constatare INTEGER DEFAULT 0,
    este_garantie INTEGER DEFAULT 0,
    
    client_id INTEGER,
    client_nume_text TEXT, -- Stocam si numele textual in caz ca e client nou
    locatie TEXT,
    solicitare_client TEXT,
    
    utilaj TEXT,
    serie_utilaj TEXT,
    ore_funct INTEGER,
    
    operatii_efectuate TEXT,
    observatii TEXT,
    
    manopera_ore REAL,
    km_efectuati INTEGER,
    
    nume_semnatura_client TEXT,
    plecare TEXT,
    destinatie TEXT,
    retur INTEGER,
    
    FOREIGN KEY (client_id) REFERENCES Clienti(id)
);

-- Tabel "pivot" pentru piesele inlocuite (legate de un raport)
CREATE TABLE IF NOT EXISTS PieseInlocuite (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raport_id INTEGER NOT NULL,
    pn TEXT,
    descriere TEXT,
    buc INTEGER,
    FOREIGN KEY (raport_id) REFERENCES Rapoarte(id)
);

-- Tabel "pivot" pentru piesele necesare
CREATE TABLE IF NOT EXISTS PieseNecesare (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raport_id INTEGER NOT NULL,
    pn TEXT,
    descriere TEXT,
    buc INTEGER,
    FOREIGN KEY (raport_id) REFERENCES Rapoarte(id)
);

CREATE TABLE IF NOT EXISTS Manopera (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raport_id INTEGER NOT NULL,
    tip TEXT,
    ore REAL,
    FOREIGN KEY (raport_id) REFERENCES Rapoarte(id)
);

CREATE TABLE IF NOT EXISTS Destinatii (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nume TEXT NOT NULL UNIQUE
);

-- Introducem cativa clienti si piese de test
INSERT OR IGNORE INTO Clienti (nume, cui) VALUES ('Client Exemplu SRL', 'RO123456');
INSERT OR IGNORE INTO Clienti (nume, cui) VALUES ('Alt Client SA', 'RO654321');
INSERT OR IGNORE INTO PieseMaster (pn, descriere) VALUES ('F-102-300', 'Filtru ulei');
INSERT OR IGNORE INTO PieseMaster (pn, descriere) VALUES ('S-500-A', 'Senzor presiune');

CREATE TABLE IF NOT EXISTS Companie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nume TEXT,
    adresa TEXT,
    email TEXT,
    telefon TEXT,
    logo TEXT
);

INSERT OR IGNORE INTO Companie (id, nume, adresa, email, telefon, logo) VALUES (1, 'NUME COMPANIE', 'Adresa Companie, Oras, Cod Postal', 'contact@companie.ro', '07xx xxx xxx', 'logo.png');

CREATE TABLE IF NOT EXISTS Lucrare (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);