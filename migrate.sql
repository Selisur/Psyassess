CREATE TYPE mc3 AS ENUM ('Nein', 'Vielleicht', 'Ja');

CREATE TYPE mc5 AS ENUM ('Nie', 'Selten', 'Manchmal', 'Oft', 'Sehr oft');

CREATE TYPE fragentyp AS ENUM ('a1','a2','a3');

CREATE TABLE Patient (
	ID integer PRIMARY KEY GENERATED ALWAYS AS identity,
	beigetreten DATE DEFAULT current_timestamp NOT NULL,
	vornamen varchar(60) NOT NULL,
	nachnamen varchar(60) NOT NULL,
	email varchar(100) NOT NULL UNIQUE
);

CREATE TABLE token (
	hash varchar(65) PRIMARY KEY,
	Patient_ID integer NOT NULL  REFERENCES Patient (ID) ON DELETE CASCADE,
	created timestamptz NOT NULL DEFAULT now() NOT NULL,
	expires_at timestamptz NOT NULL DEFAULT now() + interval '2 days' NOT NULL
	);
	
CREATE TABLE session (
	hash varchar(65) PRIMARY KEY,
	Patient_ID integer NOT NULL REFERENCES Patient (ID)  ON DELETE CASCADE,
	created timestamptz NOT NULL DEFAULT now() NOT NULL,
	expires_at timestamptz NOT NULL DEFAULT now() + interval '2 hours' NOT NULL
	);
	
CREATE TABLE Test (
	ID integer PRIMARY KEY GENERATED ALWAYS AS identity,
	Patient_ID integer REFERENCES Patient (ID) NOT NULL,
	eingereicht DATE DEFAULT current_timestamp NOT NULL, 
	Ergebnis varchar(1000) NOT NULL
);

CREATE TABLE Frage (
	ID varchar(3) PRIMARY KEY,
	Typ fragentyp NOT NULL,
	Text varchar(1000) NOT NULL
	);
	
	
CREATE TABLE Antwort (
	ID integer PRIMARY KEY GENERATED ALWAYS AS identity, 
	Test_ID integer NOT NULL REFERENCES Test (ID) ,
	Frage_ID varchar(3) NOT NULL REFERENCES Frage (ID) ,
	a1 mc3,
	a2 mc5,
	a3 varchar(1000),
	CHECK (num_nonnulls(a1,a2,a3) = 1)
);

CREATE TABLE raw_import (data jsonb);



\copy raw_import (data) FROM 'gen_catalog.json';
insert into frage (id, typ, text) 
select t.id, 'a1', t.text 
from raw_import, 
jsonb_to_recordset(data) as t(id varchar(3), text varchar(1000));

delete from raw_import;



\copy raw_import (data) FROM 'adhs_catalog.json';
insert into frage (id, typ, text) 
select t.id, 'a2', t.text 
from raw_import, 
jsonb_to_recordset(data) as t(id varchar(3), text varchar(1000));

delete from raw_import;


\copy raw_import (data) FROM 'free_catalog.json';
insert into frage (id, typ, text) 
select t.id, 'a3', t.text 
from raw_import, 
jsonb_to_recordset(data) as t(id varchar(3), text varchar(1000));

delete from raw_import;
