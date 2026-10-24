BEGIN TRANSACTION;
CREATE TABLE administrateurs (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    login               TEXT NOT NULL UNIQUE,
    mot_de_passe_hash   TEXT NOT NULL               -- généré avec werkzeug.security.generate_password_hash
);
INSERT INTO "administrateurs" VALUES(1,'admin','scrypt:32768:8:1$5hGd32ZTGzGehh1Y$e92a7b5fa5de560438fb639538bc8791eff258525c68622f59689b8ddb7dc279ae713216903b9f6fce4b29a3d64275784b359a8f5cf12d5ee3f9f02b5577255b');
CREATE TABLE medecins (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nom                 TEXT NOT NULL,
    specialite          TEXT NOT NULL,
    photo               TEXT,                       -- nom du fichier dans static/images/
    jours_consultation  TEXT NOT NULL
        CHECK (jours_consultation GLOB '[1-7]*' AND jours_consultation NOT GLOB '*[^1-7,]*')
);
INSERT INTO "medecins" VALUES(1,'Dr Jean-Pierre Mbarga','Médecine générale','dr_mbarga.jpg','1,2,3,4,5');
INSERT INTO "medecins" VALUES(2,'Dr Estelle Nkoulou','Médecine générale','dr_nkoulou.jpg','1,3,5');
INSERT INTO "medecins" VALUES(3,'Dr Alain Fotso','Cardiologie','dr_fotso.jpg','2,4');
INSERT INTO "medecins" VALUES(4,'Dr Carine Tchamba','Cardiologie','dr_tchamba.jpg','1,3,6');
INSERT INTO "medecins" VALUES(5,'Dr Paul Essomba','Pédiatrie','dr_essomba.jpg','1,2,4,5');
INSERT INTO "medecins" VALUES(6,'Dr Mireille Ekambi','Pédiatrie','dr_ekambi.jpg','3,4,6');
INSERT INTO "medecins" VALUES(7,'Dr Serge Kamdem','Dermatologie','dr_kamdem.jpg','2,3,5');
INSERT INTO "medecins" VALUES(8,'Dr Brenda Ngwa','Dermatologie','dr_ngwa.jpg','1,4,5');
CREATE TABLE patients (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nom             TEXT NOT NULL,
    prenom          TEXT NOT NULL,
    telephone       TEXT NOT NULL UNIQUE,           -- format normalisé : 6XXXXXXXX (9 chiffres)
    date_naissance  TEXT NOT NULL,                  -- AAAA-MM-JJ
    ville           TEXT NOT NULL,
    date_creation   TEXT NOT NULL DEFAULT (date('now'))   -- sert aux stats "nouveaux patients par semaine"
);
INSERT INTO "patients" VALUES(1,'Dikongue','Ornella','655886458','2008-01-24','Bafoussam','2026-10-23');
INSERT INTO "patients" VALUES(2,'Tabi','Brice','650618486','1971-07-12','Yaoundé','2026-09-20');
INSERT INTO "patients" VALUES(3,'Owona','Annie','690895035','1981-03-11','Douala','2026-09-24');
INSERT INTO "patients" VALUES(4,'Wouambo','Sandrine','680073435','2013-02-26','Douala','2026-10-05');
INSERT INTO "patients" VALUES(5,'Dikongue','Martial','696358595','2017-04-19','Douala','2026-09-30');
INSERT INTO "patients" VALUES(6,'Tchamba','Alain','697816442','2013-03-21','Douala','2026-10-24');
INSERT INTO "patients" VALUES(7,'Ndam','Arnaud','699249566','1992-02-11','Douala','2026-10-04');
INSERT INTO "patients" VALUES(8,'Manga','Clarisse','651189893','1950-10-31','Douala','2026-09-22');
INSERT INTO "patients" VALUES(9,'Njock','Prisca','696859839','1995-11-14','Douala','2026-10-24');
INSERT INTO "patients" VALUES(10,'Owona','Ornella','671984024','1990-08-20','Douala','2026-10-24');
INSERT INTO "patients" VALUES(11,'Njoya','Brenda','650045861','1990-04-26','Douala','2026-10-24');
INSERT INTO "patients" VALUES(12,'Manga','Boris','690135794','2009-12-21','Limbé','2026-09-20');
INSERT INTO "patients" VALUES(13,'Ndongo','Boris','670985069','1992-06-07','Bonabéri','2026-10-24');
INSERT INTO "patients" VALUES(14,'Ndzie','Brenda','697839308','1963-04-30','Yaoundé','2026-10-15');
INSERT INTO "patients" VALUES(15,'Nkoulou','Marie','696333195','1995-10-16','Douala','2026-09-30');
INSERT INTO "patients" VALUES(16,'Atangana','Ornella','681427506','1988-11-25','Douala','2026-09-19');
INSERT INTO "patients" VALUES(17,'Tchamba','Chantal','675460628','1990-07-15','Douala','2026-09-15');
INSERT INTO "patients" VALUES(18,'Ndzie','Nadège','694583114','1974-06-23','Bafoussam','2026-09-30');
INSERT INTO "patients" VALUES(19,'Njock','Éric','681545520','1965-11-16','Douala','2026-09-30');
INSERT INTO "patients" VALUES(20,'Njock','Carine','681478693','2007-12-05','Douala','2026-09-16');
INSERT INTO "patients" VALUES(21,'Ebanda','Joëlle','655627755','1969-06-05','Yaoundé','2026-09-29');
INSERT INTO "patients" VALUES(22,'Owona','Serge','694167716','1958-08-26','Douala','2026-09-22');
INSERT INTO "patients" VALUES(23,'Essomba','Joëlle','681120892','1976-02-10','Douala','2026-10-24');
INSERT INTO "patients" VALUES(24,'Nkoulou','Rosine','655059834','1977-10-21','Édéa','2026-09-16');
INSERT INTO "patients" VALUES(25,'Fotso','Yannick','681654613','1986-04-06','Douala','2026-10-01');
INSERT INTO "patients" VALUES(26,'Ndzie','Rodrigue','690078237','1976-03-09','Bafoussam','2026-10-16');
INSERT INTO "patients" VALUES(27,'Kouam','Serge','694395357','2018-11-22','Douala','2026-09-16');
INSERT INTO "patients" VALUES(28,'Ngwa','Mireille','670559341','1953-05-07','Douala','2026-10-11');
INSERT INTO "patients" VALUES(29,'Youmbi','Rosine','677710755','1987-10-08','Douala','2026-09-23');
INSERT INTO "patients" VALUES(30,'Nkoulou','Hervé','678549160','1951-06-28','Douala','2026-09-23');
INSERT INTO "patients" VALUES(31,'Owona','Ulrich','697736094','1980-07-26','Douala','2026-10-19');
INSERT INTO "patients" VALUES(32,'Simo','Alain','690928323','1985-10-20','Édéa','2026-09-29');
INSERT INTO "patients" VALUES(33,'Ndam','Prisca','680161898','2002-02-01','Douala','2026-09-17');
INSERT INTO "patients" VALUES(34,'Tsafack','Paul','652252719','1965-06-25','Bonabéri','2026-09-25');
INSERT INTO "patients" VALUES(35,'Kouam','Joëlle','651939561','2001-05-16','Douala','2026-09-19');
INSERT INTO "patients" VALUES(36,'Ngassa','Sandrine','681537618','1984-12-01','Douala','2026-10-18');
INSERT INTO "patients" VALUES(37,'Kamga','Michèle','675968693','1984-11-12','Bafoussam','2026-09-20');
INSERT INTO "patients" VALUES(38,'Tagne','Boris','697031016','2014-10-09','Kribi','2026-09-27');
INSERT INTO "patients" VALUES(39,'Etoundi','Jean','690355213','1955-09-16','Douala','2026-10-20');
INSERT INTO "patients" VALUES(40,'Ndzie','Patrick','680639158','1973-07-22','Yaoundé','2026-09-14');
INSERT INTO "patients" VALUES(41,'Mvondo','Brice','652704372','1957-05-28','Douala','2026-09-21');
INSERT INTO "patients" VALUES(42,'Djomo','Chantal','696418263','1978-12-14','Douala','2026-10-24');
INSERT INTO "patients" VALUES(43,'Ndzie','Joëlle','670457431','1969-02-05','Douala','2026-10-01');
INSERT INTO "patients" VALUES(44,'Owona','Arnaud','699629512','1963-01-16','Douala','2026-09-21');
INSERT INTO "patients" VALUES(45,'Nkoulou','Thierry','681636998','1999-04-27','Yaoundé','2026-10-24');
INSERT INTO "patients" VALUES(46,'Atangana','Ulrich','690603127','1988-01-29','Douala','2026-10-12');
INSERT INTO "patients" VALUES(47,'Ayissi','Danielle','696840766','2019-10-26','Douala','2026-09-30');
INSERT INTO "patients" VALUES(48,'Njock','Julienne','678635179','1996-03-13','Douala','2026-10-24');
INSERT INTO "patients" VALUES(49,'Njock','Rosine','671704551','1968-07-07','Douala','2026-09-28');
INSERT INTO "patients" VALUES(50,'Fotso','Brenda','699799963','1966-08-15','Douala','2026-10-19');
CREATE TABLE rendez_vous (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id  INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    medecin_id  INTEGER NOT NULL REFERENCES medecins(id) ON DELETE RESTRICT,
    date        TEXT NOT NULL,                      -- AAAA-MM-JJ
    heure       TEXT NOT NULL
        CHECK (heure IN ('08:00','08:30','09:00','09:30','10:00','10:30','11:00','11:30')),
    motif       TEXT NOT NULL,
    statut      TEXT NOT NULL DEFAULT 'prevu'
        CHECK (statut IN ('prevu','effectue','annule')),
    date_prise  TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (medecin_id, date, heure)
);
INSERT INTO "rendez_vous" VALUES(1,12,3,'2026-09-29','08:30','Électrocardiogramme','effectue','2026-09-20 13:17:00');
INSERT INTO "rendez_vous" VALUES(2,43,7,'2026-11-06','10:00','Contrôle d''un grain de beauté','prevu','2026-10-24 16:07:00');
INSERT INTO "rendez_vous" VALUES(3,43,3,'2026-10-15','10:00','Douleurs thoraciques','effectue','2026-10-08 09:51:00');
INSERT INTO "rendez_vous" VALUES(4,1,6,'2026-10-24','08:00','Fièvre de l''enfant','prevu','2026-10-23 12:48:00');
INSERT INTO "rendez_vous" VALUES(5,35,4,'2026-10-21','08:30','Essoufflement à l''effort','effectue','2026-10-20 11:45:00');
INSERT INTO "rendez_vous" VALUES(6,49,6,'2026-11-04','09:30','Visite de contrôle','prevu','2026-10-24 13:56:00');
INSERT INTO "rendez_vous" VALUES(7,48,4,'2026-11-02','08:00','Électrocardiogramme','prevu','2026-10-24 18:41:00');
INSERT INTO "rendez_vous" VALUES(8,47,1,'2026-10-01','08:00','Consultation générale','effectue','2026-09-30 12:39:00');
INSERT INTO "rendez_vous" VALUES(9,28,4,'2026-10-14','10:30','Suivi cardiaque','effectue','2026-10-11 16:40:00');
INSERT INTO "rendez_vous" VALUES(10,26,5,'2026-10-20','08:00','Suivi de croissance','effectue','2026-10-16 16:25:00');
INSERT INTO "rendez_vous" VALUES(11,2,1,'2026-09-28','09:30','Paludisme (suspicion)','effectue','2026-09-20 18:39:00');
INSERT INTO "rendez_vous" VALUES(12,25,1,'2026-10-08','10:00','Paludisme (suspicion)','effectue','2026-10-01 12:41:00');
INSERT INTO "rendez_vous" VALUES(13,24,4,'2026-09-26','10:30','Contrôle de la tension','effectue','2026-09-16 16:49:00');
INSERT INTO "rendez_vous" VALUES(14,45,7,'2026-10-30','09:00','Contrôle d''un grain de beauté','prevu','2026-10-24 10:31:00');
INSERT INTO "rendez_vous" VALUES(15,20,1,'2026-09-24','08:30','Bilan de santé','effectue','2026-09-16 18:26:00');
INSERT INTO "rendez_vous" VALUES(16,25,4,'2026-10-21','10:30','Électrocardiogramme','effectue','2026-10-16 11:07:00');
INSERT INTO "rendez_vous" VALUES(17,32,7,'2026-10-16','10:00','Eczéma','effectue','2026-10-06 10:19:00');
INSERT INTO "rendez_vous" VALUES(18,31,1,'2026-11-04','08:30','Suivi hypertension','prevu','2026-10-24 17:32:00');
INSERT INTO "rendez_vous" VALUES(19,21,1,'2026-10-06','10:00','Suivi hypertension','effectue','2026-09-29 12:01:00');
INSERT INTO "rendez_vous" VALUES(20,32,5,'2026-10-09','10:30','Fièvre de l''enfant','annule','2026-09-29 09:06:00');
INSERT INTO "rendez_vous" VALUES(21,37,7,'2026-10-28','11:00','Mycose','prevu','2026-10-20 15:46:00');
INSERT INTO "rendez_vous" VALUES(22,40,2,'2026-11-18','09:30','Fatigue inhabituelle','prevu','2026-10-24 10:06:00');
INSERT INTO "rendez_vous" VALUES(23,7,1,'2026-10-13','10:00','Bilan de santé','effectue','2026-10-06 11:55:00');
INSERT INTO "rendez_vous" VALUES(24,29,1,'2026-10-02','08:30','Fatigue inhabituelle','effectue','2026-09-23 14:13:00');
INSERT INTO "rendez_vous" VALUES(25,50,2,'2026-11-04','09:30','Paludisme (suspicion)','prevu','2026-10-24 15:15:00');
INSERT INTO "rendez_vous" VALUES(26,44,4,'2026-09-28','09:30','Contrôle de la tension','effectue','2026-09-21 18:37:00');
INSERT INTO "rendez_vous" VALUES(27,49,3,'2026-11-05','10:30','Suivi cardiaque','annule','2026-10-24 08:51:00');
INSERT INTO "rendez_vous" VALUES(28,16,4,'2026-11-04','09:30','Essoufflement à l''effort','prevu','2026-10-24 16:18:00');
INSERT INTO "rendez_vous" VALUES(29,39,7,'2026-11-10','09:00','Démangeaisons','prevu','2026-10-24 11:00:00');
INSERT INTO "rendez_vous" VALUES(30,39,4,'2026-10-24','09:00','Électrocardiogramme','prevu','2026-10-20 16:37:00');
INSERT INTO "rendez_vous" VALUES(31,40,3,'2026-09-24','08:30','Contrôle de la tension','effectue','2026-09-14 14:30:00');
INSERT INTO "rendez_vous" VALUES(32,22,1,'2026-10-02','09:30','Fatigue inhabituelle','annule','2026-09-22 13:40:00');
INSERT INTO "rendez_vous" VALUES(33,8,8,'2026-11-09','08:30','Éruption cutanée','prevu','2026-10-24 09:56:00');
INSERT INTO "rendez_vous" VALUES(34,21,6,'2026-11-12','10:30','Diarrhée','prevu','2026-10-24 11:55:00');
INSERT INTO "rendez_vous" VALUES(35,41,7,'2026-10-20','08:00','Démangeaisons','annule','2026-10-16 10:28:00');
INSERT INTO "rendez_vous" VALUES(36,3,8,'2026-10-01','11:00','Eczéma','effectue','2026-09-28 09:01:00');
INSERT INTO "rendez_vous" VALUES(37,3,4,'2026-09-30','08:00','Électrocardiogramme','effectue','2026-09-24 09:03:00');
INSERT INTO "rendez_vous" VALUES(38,17,1,'2026-11-19','10:30','Bilan de santé','prevu','2026-10-24 14:06:00');
INSERT INTO "rendez_vous" VALUES(39,40,8,'2026-09-24','10:00','Acné','effectue','2026-09-17 09:44:00');
INSERT INTO "rendez_vous" VALUES(40,16,3,'2026-10-01','10:30','Électrocardiogramme','annule','2026-09-21 12:20:00');
INSERT INTO "rendez_vous" VALUES(41,37,7,'2026-11-06','10:30','Démangeaisons','prevu','2026-10-24 10:33:00');
INSERT INTO "rendez_vous" VALUES(42,9,2,'2026-11-04','10:00','Suivi hypertension','prevu','2026-10-24 12:13:00');
INSERT INTO "rendez_vous" VALUES(43,26,1,'2026-11-10','09:00','Maux de tête fréquents','prevu','2026-10-24 11:00:00');
INSERT INTO "rendez_vous" VALUES(44,48,5,'2026-10-30','10:30','Suivi de croissance','prevu','2026-10-24 18:21:00');
INSERT INTO "rendez_vous" VALUES(45,9,5,'2026-11-13','10:30','Visite de contrôle','prevu','2026-10-24 14:48:00');
INSERT INTO "rendez_vous" VALUES(46,41,3,'2026-10-29','09:00','Palpitations','annule','2026-10-23 14:47:00');
INSERT INTO "rendez_vous" VALUES(47,10,6,'2026-11-21','09:00','Visite de contrôle','prevu','2026-10-24 17:01:00');
INSERT INTO "rendez_vous" VALUES(48,11,2,'2026-11-04','08:30','Douleurs abdominales','prevu','2026-10-24 12:24:00');
INSERT INTO "rendez_vous" VALUES(49,13,7,'2026-11-17','08:30','Éruption cutanée','prevu','2026-10-24 11:11:00');
INSERT INTO "rendez_vous" VALUES(50,31,5,'2026-11-23','10:30','Vaccination','prevu','2026-10-24 18:39:00');
INSERT INTO "rendez_vous" VALUES(51,40,2,'2026-10-02','09:30','Fièvre persistante','annule','2026-09-30 09:50:00');
INSERT INTO "rendez_vous" VALUES(52,30,8,'2026-11-16','08:00','Mycose','prevu','2026-10-24 08:48:00');
INSERT INTO "rendez_vous" VALUES(53,38,3,'2026-11-03','09:30','Contrôle de la tension','prevu','2026-10-24 14:19:00');
INSERT INTO "rendez_vous" VALUES(54,8,6,'2026-09-30','10:00','Visite de contrôle','effectue','2026-09-22 15:40:00');
INSERT INTO "rendez_vous" VALUES(55,33,1,'2026-09-24','08:00','Suivi hypertension','effectue','2026-09-17 11:17:00');
INSERT INTO "rendez_vous" VALUES(56,18,4,'2026-10-05','08:30','Douleurs thoraciques','effectue','2026-09-30 08:56:00');
INSERT INTO "rendez_vous" VALUES(57,43,2,'2026-10-23','09:30','Fièvre persistante','effectue','2026-10-22 13:36:00');
INSERT INTO "rendez_vous" VALUES(58,15,2,'2026-10-12','09:00','Fatigue inhabituelle','annule','2026-10-03 16:07:00');
INSERT INTO "rendez_vous" VALUES(59,43,1,'2026-10-14','09:00','Maux de tête fréquents','effectue','2026-10-11 10:09:00');
INSERT INTO "rendez_vous" VALUES(60,15,5,'2026-10-06','10:00','Fièvre de l''enfant','effectue','2026-09-30 11:12:00');
INSERT INTO "rendez_vous" VALUES(61,50,8,'2026-10-29','10:30','Contrôle d''un grain de beauté','prevu','2026-10-19 12:51:00');
INSERT INTO "rendez_vous" VALUES(62,34,1,'2026-11-12','08:30','Consultation générale','prevu','2026-10-24 18:58:00');
INSERT INTO "rendez_vous" VALUES(63,30,7,'2026-10-06','09:30','Éruption cutanée','effectue','2026-10-04 11:19:00');
INSERT INTO "rendez_vous" VALUES(64,6,2,'2026-11-13','08:30','Consultation générale','prevu','2026-10-24 12:08:00');
INSERT INTO "rendez_vous" VALUES(65,19,7,'2026-10-16','08:30','Éruption cutanée','effectue','2026-10-12 16:00:00');
INSERT INTO "rendez_vous" VALUES(66,5,8,'2026-10-08','09:00','Démangeaisons','annule','2026-09-30 16:53:00');
INSERT INTO "rendez_vous" VALUES(67,38,5,'2026-11-23','09:30','Visite de contrôle','annule','2026-10-24 15:59:00');
INSERT INTO "rendez_vous" VALUES(68,36,4,'2026-10-26','10:30','Palpitations','prevu','2026-10-20 11:34:00');
INSERT INTO "rendez_vous" VALUES(69,13,5,'2026-11-20','09:30','Vaccination','prevu','2026-10-24 18:41:00');
INSERT INTO "rendez_vous" VALUES(70,37,3,'2026-09-29','08:00','Essoufflement à l''effort','effectue','2026-09-21 14:07:00');
INSERT INTO "rendez_vous" VALUES(71,44,7,'2026-10-21','10:00','Acné','annule','2026-10-14 11:41:00');
INSERT INTO "rendez_vous" VALUES(72,33,2,'2026-10-09','10:30','Bilan de santé','annule','2026-10-08 16:30:00');
INSERT INTO "rendez_vous" VALUES(73,45,1,'2026-11-20','08:30','Certificat médical','prevu','2026-10-24 10:19:00');
INSERT INTO "rendez_vous" VALUES(74,31,2,'2026-10-26','08:30','Maux de tête fréquents','prevu','2026-10-19 13:55:00');
INSERT INTO "rendez_vous" VALUES(75,42,5,'2026-11-17','09:00','Vaccination','prevu','2026-10-24 13:35:00');
INSERT INTO "rendez_vous" VALUES(76,49,7,'2026-11-18','08:00','Mycose','prevu','2026-10-24 11:59:00');
INSERT INTO "rendez_vous" VALUES(77,33,5,'2026-11-13','08:00','Vaccination','prevu','2026-10-24 09:40:00');
INSERT INTO "rendez_vous" VALUES(78,42,2,'2026-11-20','10:30','Certificat médical','prevu','2026-10-24 16:32:00');
INSERT INTO "rendez_vous" VALUES(79,27,6,'2026-10-24','10:30','Fièvre de l''enfant','prevu','2026-10-22 08:33:00');
INSERT INTO "rendez_vous" VALUES(80,7,2,'2026-10-19','10:30','Douleurs abdominales','effectue','2026-10-14 17:43:00');
INSERT INTO "rendez_vous" VALUES(81,43,1,'2026-10-20','10:00','Fièvre persistante','effectue','2026-10-15 15:33:00');
INSERT INTO "rendez_vous" VALUES(82,19,6,'2026-10-03','09:00','Diarrhée','effectue','2026-09-30 14:05:00');
INSERT INTO "rendez_vous" VALUES(83,30,3,'2026-09-24','08:00','Palpitations','annule','2026-09-23 08:40:00');
INSERT INTO "rendez_vous" VALUES(84,17,5,'2026-09-25','08:00','Vaccination','effectue','2026-09-15 09:28:00');
INSERT INTO "rendez_vous" VALUES(85,36,2,'2026-11-23','09:30','Suivi hypertension','prevu','2026-10-24 08:23:00');
INSERT INTO "rendez_vous" VALUES(86,16,1,'2026-09-28','10:00','Certificat médical','effectue','2026-09-19 09:57:00');
INSERT INTO "rendez_vous" VALUES(87,29,8,'2026-10-22','08:30','Éruption cutanée','effectue','2026-10-18 13:05:00');
INSERT INTO "rendez_vous" VALUES(88,27,1,'2026-09-25','08:30','Maux de tête fréquents','effectue','2026-09-24 12:00:00');
INSERT INTO "rendez_vous" VALUES(89,27,1,'2026-09-24','09:30','Certificat médical','effectue','2026-09-16 09:56:00');
INSERT INTO "rendez_vous" VALUES(90,14,4,'2026-10-19','09:00','Contrôle de la tension','effectue','2026-10-15 08:05:00');
INSERT INTO "rendez_vous" VALUES(91,18,6,'2026-11-19','09:30','Visite de contrôle','prevu','2026-10-24 15:38:00');
INSERT INTO "rendez_vous" VALUES(92,26,1,'2026-11-18','10:00','Suivi hypertension','prevu','2026-10-24 11:12:00');
INSERT INTO "rendez_vous" VALUES(93,7,1,'2026-10-06','08:30','Fièvre persistante','effectue','2026-10-04 13:35:00');
INSERT INTO "rendez_vous" VALUES(94,34,1,'2026-11-16','08:30','Certificat médical','prevu','2026-10-24 08:42:00');
INSERT INTO "rendez_vous" VALUES(95,19,4,'2026-10-19','10:00','Contrôle de la tension','effectue','2026-10-18 14:25:00');
INSERT INTO "rendez_vous" VALUES(96,41,6,'2026-10-01','09:30','Toux persistante','effectue','2026-09-22 10:57:00');
INSERT INTO "rendez_vous" VALUES(97,24,5,'2026-10-15','10:30','Visite de contrôle','annule','2026-10-10 09:29:00');
INSERT INTO "rendez_vous" VALUES(98,2,8,'2026-11-13','09:00','Acné','prevu','2026-10-24 14:51:00');
INSERT INTO "rendez_vous" VALUES(99,16,4,'2026-10-07','10:30','Essoufflement à l''effort','effectue','2026-10-04 08:33:00');
INSERT INTO "rendez_vous" VALUES(100,47,7,'2026-10-06','10:00','Mycose','annule','2026-10-03 08:47:00');
INSERT INTO "rendez_vous" VALUES(101,8,1,'2026-10-08','09:30','Bilan de santé','effectue','2026-10-07 18:51:00');
INSERT INTO "rendez_vous" VALUES(102,37,1,'2026-09-29','08:30','Fatigue inhabituelle','effectue','2026-09-20 17:42:00');
INSERT INTO "rendez_vous" VALUES(103,35,3,'2026-10-27','08:00','Douleurs thoraciques','prevu','2026-10-18 08:52:00');
INSERT INTO "rendez_vous" VALUES(104,7,2,'2026-11-18','09:00','Certificat médical','prevu','2026-10-24 17:23:00');
INSERT INTO "rendez_vous" VALUES(105,4,6,'2026-10-08','11:30','Visite de contrôle','effectue','2026-10-05 15:25:00');
INSERT INTO "rendez_vous" VALUES(106,32,1,'2026-11-09','10:30','Paludisme (suspicion)','prevu','2026-10-24 18:06:00');
INSERT INTO "rendez_vous" VALUES(107,19,1,'2026-11-10','11:00','Paludisme (suspicion)','annule','2026-10-24 08:10:00');
INSERT INTO "rendez_vous" VALUES(108,26,2,'2026-10-23','11:00','Maux de tête fréquents','effectue','2026-10-17 11:16:00');
INSERT INTO "rendez_vous" VALUES(109,4,1,'2026-10-20','10:30','Bilan de santé','effectue','2026-10-19 09:12:00');
INSERT INTO "rendez_vous" VALUES(110,38,1,'2026-09-29','10:30','Fièvre persistante','effectue','2026-09-27 15:04:00');
INSERT INTO "rendez_vous" VALUES(111,25,1,'2026-10-19','10:30','Bilan de santé','effectue','2026-10-12 13:35:00');
INSERT INTO "rendez_vous" VALUES(112,33,1,'2026-11-12','10:00','Maux de tête fréquents','annule','2026-10-24 13:16:00');
INSERT INTO "rendez_vous" VALUES(113,29,1,'2026-09-30','10:30','Consultation générale','effectue','2026-09-27 10:22:00');
INSERT INTO "rendez_vous" VALUES(114,27,1,'2026-10-26','08:00','Fatigue inhabituelle','prevu','2026-10-24 09:17:00');
INSERT INTO "rendez_vous" VALUES(115,23,7,'2026-11-10','08:00','Contrôle d''un grain de beauté','prevu','2026-10-24 12:07:00');
INSERT INTO "rendez_vous" VALUES(116,7,1,'2026-11-10','08:30','Maux de tête fréquents','prevu','2026-10-24 18:04:00');
INSERT INTO "rendez_vous" VALUES(117,21,3,'2026-10-08','09:00','Essoufflement à l''effort','effectue','2026-10-04 16:56:00');
INSERT INTO "rendez_vous" VALUES(118,44,5,'2026-10-16','10:00','Visite de contrôle','effectue','2026-10-09 08:18:00');
INSERT INTO "rendez_vous" VALUES(119,46,1,'2026-10-21','10:00','Paludisme (suspicion)','effectue','2026-10-12 13:18:00');
INSERT INTO "rendez_vous" VALUES(120,49,2,'2026-11-20','09:00','Paludisme (suspicion)','prevu','2026-10-24 18:45:00');
INSERT INTO "rendez_vous" VALUES(121,49,5,'2026-11-17','10:30','Toux persistante','prevu','2026-10-24 14:02:00');
INSERT INTO "rendez_vous" VALUES(122,46,7,'2026-11-18','08:30','Mycose','prevu','2026-10-24 08:42:00');
INSERT INTO "rendez_vous" VALUES(123,11,3,'2026-10-27','09:00','Douleurs thoraciques','prevu','2026-10-24 17:26:00');
INSERT INTO "rendez_vous" VALUES(124,7,3,'2026-10-22','08:30','Contrôle de la tension','effectue','2026-10-14 18:38:00');
INSERT INTO "rendez_vous" VALUES(125,15,3,'2026-11-17','08:00','Palpitations','prevu','2026-10-24 14:18:00');
INSERT INTO "rendez_vous" VALUES(126,26,2,'2026-11-09','08:00','Bilan de santé','prevu','2026-10-24 10:01:00');
INSERT INTO "rendez_vous" VALUES(127,22,3,'2026-10-20','09:00','Douleurs thoraciques','effectue','2026-10-13 18:58:00');
INSERT INTO "rendez_vous" VALUES(128,46,4,'2026-10-24','09:30','Douleurs thoraciques','prevu','2026-10-17 12:34:00');
INSERT INTO "rendez_vous" VALUES(129,41,4,'2026-11-02','10:30','Contrôle de la tension','prevu','2026-10-24 17:27:00');
INSERT INTO "rendez_vous" VALUES(130,35,6,'2026-09-26','10:00','Fièvre de l''enfant','effectue','2026-09-19 17:21:00');
INSERT INTO "rendez_vous" VALUES(131,8,6,'2026-11-14','08:00','Diarrhée','prevu','2026-10-24 17:33:00');
INSERT INTO "rendez_vous" VALUES(132,34,1,'2026-11-09','09:00','Certificat médical','prevu','2026-10-24 08:05:00');
INSERT INTO "rendez_vous" VALUES(133,17,8,'2026-10-02','10:00','Éruption cutanée','effectue','2026-09-24 16:09:00');
INSERT INTO "rendez_vous" VALUES(134,2,5,'2026-10-09','09:00','Suivi de croissance','effectue','2026-10-01 15:17:00');
INSERT INTO "rendez_vous" VALUES(135,44,5,'2026-10-06','09:30','Vaccination','effectue','2026-09-28 17:10:00');
INSERT INTO "rendez_vous" VALUES(136,5,2,'2026-11-16','08:30','Certificat médical','prevu','2026-10-24 12:28:00');
INSERT INTO "rendez_vous" VALUES(137,35,3,'2026-11-03','08:30','Contrôle de la tension','prevu','2026-10-24 17:02:00');
INSERT INTO "rendez_vous" VALUES(138,41,2,'2026-09-30','09:30','Paludisme (suspicion)','effectue','2026-09-21 14:37:00');
INSERT INTO "rendez_vous" VALUES(139,43,8,'2026-10-05','08:00','Contrôle d''un grain de beauté','effectue','2026-10-01 09:11:00');
INSERT INTO "rendez_vous" VALUES(140,13,2,'2026-10-30','10:30','Bilan de santé','annule','2026-10-24 18:47:00');
INSERT INTO "rendez_vous" VALUES(141,35,1,'2026-10-09','09:00','Fatigue inhabituelle','effectue','2026-10-02 13:31:00');
INSERT INTO "rendez_vous" VALUES(142,25,2,'2026-10-19','08:00','Fièvre persistante','effectue','2026-10-14 13:00:00');
INSERT INTO "rendez_vous" VALUES(143,19,1,'2026-10-27','09:00','Fatigue inhabituelle','prevu','2026-10-17 14:23:00');
INSERT INTO "rendez_vous" VALUES(144,44,2,'2026-11-18','08:00','Fièvre persistante','annule','2026-10-24 16:20:00');
INSERT INTO "rendez_vous" VALUES(145,24,7,'2026-11-04','08:00','Mycose','prevu','2026-10-24 09:51:00');
INSERT INTO "rendez_vous" VALUES(146,36,3,'2026-10-22','08:00','Essoufflement à l''effort','effectue','2026-10-18 15:32:00');
INSERT INTO "rendez_vous" VALUES(147,10,7,'2026-11-10','10:30','Éruption cutanée','prevu','2026-10-24 14:04:00');
INSERT INTO "rendez_vous" VALUES(148,24,1,'2026-10-05','09:00','Certificat médical','effectue','2026-09-30 12:19:00');
INSERT INTO "rendez_vous" VALUES(149,49,1,'2026-10-02','11:30','Paludisme (suspicion)','effectue','2026-09-28 17:40:00');
INSERT INTO "rendez_vous" VALUES(150,34,6,'2026-09-26','09:00','Fièvre de l''enfant','effectue','2026-09-25 18:39:00');
CREATE INDEX idx_rdv_patient ON rendez_vous(patient_id);
CREATE INDEX idx_rdv_date    ON rendez_vous(date);
CREATE INDEX idx_rdv_statut  ON rendez_vous(statut);
CREATE INDEX idx_patients_nom ON patients(nom, prenom);
CREATE INDEX idx_medecins_specialite ON medecins(specialite);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('medecins',8);
INSERT INTO "sqlite_sequence" VALUES('patients',50);
INSERT INTO "sqlite_sequence" VALUES('rendez_vous',150);
INSERT INTO "sqlite_sequence" VALUES('administrateurs',1);
COMMIT;
