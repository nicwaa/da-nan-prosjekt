PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Dikt;
DROP TABLE IF EXISTS Sesjon;
DROP TABLE IF EXISTS Bruker;

CREATE TABLE Bruker
(
	email varchar(200),
	passordhash varchar(200),
	fornavn varchar(50),
	etternavn varchar(50),
	PRIMARY KEY (email)
);

CREATE TABLE Sesjon
(
	sesjonsID varchar(200),
	email varchar(200),
	PRIMARY KEY (sesjonsID),
	FOREIGN KEY (email) REFERENCES Bruker(email)
);

CREATE TABLE Dikt
(
	diktID INTEGER PRIMARY KEY AUTOINCREMENT,
	dikt varchar(400),
	email varchar(200),
	FOREIGN KEY (email) REFERENCES Bruker(email)
);
