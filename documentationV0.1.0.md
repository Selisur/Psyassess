
# Logik


# Design

All pages in the site all share the same basic content: a heading, a info box, and a footer. Some sites additionally include form fields and buttons. there is a limited amount of CSS classes and ids (as the javascript code uses ids), which makes the design simple to understand and adjust. also changes immediately takes effect on all pages.

# Hosting

either automated install script or included in vm image:
- install python, crete virtual env, download packages, aquire secrets, start db, start uv, setup https, hardening
# Server
1. (skip: harden server)
2. install the linux VM and packages `caddy postgresql fastapi["standard"]`
3. setup the users in the VM
	- `sudo useradd -r -m -d /opt/app -s /bin/bash app`
4. download the git file
5. setup autmatic reboots:
	- for vm on machine
	- for vm on hypervisor
	- app.service, mirations.sh

Caddyfile:
```caddy
example.com {
	handle /api/* {
	reverse_proxy 127.0.0.1:8000
	}
	handle {
	root * /opt/app/frontend
	file_server
	}
}
```

/etc/systemd/system/app.service:
```bash
[Unit]
Description=FASTAPI app
After=network.target postgresql.service
Requires=postgresql.service

[Service]
User=app
WorkingDirectory=/opt/app/backend
EnvironmentFile=/opt/app/.env
ExecStartPre=/opt/spp/backend/scripts/start-pre.sh
ExecStart=uv run --frozen uvicorn main:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```


`sudo systemctl enable --now app`

# Frontend
What is seen on the website are HTML files, rendered by the Javascript frontend. 

# Backend 
FastAPI
The [[pydantic]] library and secure cookie headers enable data validation for forms and secure sessions. 
FastAPI is fast and simple.
The HTML templates are visually enhanced by few, simple [[CSS]].

# Database
The data which is inserted by users is securely and persistently stored in a [[database schema]]. This runs on my laptop currently but ultimately will be hosted on the server.
Further considerations must be made towards migrations and database security during deployment.

The webapp needs a database. Install 'postgresql' on your OS, and create the initial database repository with:
`initdb --locale=C.UTF-8 --encoding=UTF8 -D '/var/lib/postgres/data'`

Create a local user with login and create db rights and call
`createdb psyassess`

### Setup db users and give them appropriate database permissions.

modelling this is an important part of app security.

for the moment, I do it very simple.

Create a local user that can create databases.

Create a dedicated db user for the app. They need these rights:
- login
- connect to db
- use public schema?
- select, insert, update, delete on Patient, Test ...
- sequences?
```sql
for user app:
GRANT CONNECT ON DATABASE psyassess TO app;
GRANT USAGE ON SCHEMA public TO app;
connect to db:
GRANT select, insert, update, delete on all tables in schema public to app;
```

Check table permissions for a user:

`select * from information_schema.role_table_grants where grantee= 'app';`


To define the database schema, run the following calls as the database owner (local user):
```postgresql
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
```

### mitigations: question upload


```postgresql
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
```


### communicating with backend system level driver needed or not
In order to use the database in the webapp, the app needs a 
- database driver
- active [[database context]]

# Security Measures


What I have found / partially implemented is to
- minimize and validate user input.
- minimize and track dependencies of backend
- PLP with the database user. strong db account encryption. 
- HTTPS
- secure cookie headers
- strong and secure machine AC design
- server and API deny by default
- I will research and update the part
