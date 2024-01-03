
# Dockerized Django app with Postgres importing UN/LOCODE database

## 1. Setup the application
This software was developed and runs on Linux Ubuntu 18.04.4.

### 1.1. Dependencies
The following dependencies must be installed and operational on your system:
- git
- docker (19.03.9)
- docker-compose (1.25.4)

### 1.2. Download the repository
```bash
git clone https://github.com/antoine-naud/unlocode
cd unlocode
```

### 1.3. Build the images and spin up the containers
```
docker compose build
docker compose up -d
```
Below five containers should be up and running:
```bash
docker container ps -a
CONTAINER ID        IMAGE                  COMMAND                  CREATED             STATUS              PORTS                                          NAMES
5abc4348a6f9        unlocode_celery        "celery worker -A dj…"   15 seconds ago      Up 12 seconds                                                      unlocode_celery_1
126e171366ab        unlocode_celery-beat   "celery beat -A djan…"   15 seconds ago      Up 13 seconds                                                      unlocode_celery-beat_1
4d679273bfbb        unlocode_web           "sh -c 'python /code…"   15 seconds ago      Up 14 seconds       0.0.0.0:8000->8000/tcp, 0.0.0.0:8080->80/tcp   unlocode_web_1
c9bff3234b31        redis:alpine           "docker-entrypoint.s…"   16 seconds ago      Up 15 seconds       6379/tcp                                       unlocode_redis_1
0943b493a518        postgres:12.0-alpine   "docker-entrypoint.s…"   16 seconds ago      Up 14 seconds       5432/tcp                                       unlocode_db_1
```
The `web` container (named `unlocode_web_1`) will in turn:
- perform initial migration,
- execute initial import of data to `Unlocode` table in the database (the import takes about 2 minutes),
- start the Django web server.

You can check the logs of the `web` container:
```
docker-compose logs web
Attaching to unlocode_web_1
web_1          | No changes detected
web_1          | Operations to perform:
web_1          |   Apply all migrations: admin, auth, contenttypes, sessions, unlocode
web_1          | Running migrations:
web_1          |   Applying contenttypes.0001_initial... OK
web_1          |   Applying auth.0001_initial... OK
web_1          |   Applying admin.0001_initial... OK
web_1          |   Applying admin.0002_logentry_remove_auto_add... OK
web_1          |   Applying admin.0003_logentry_add_action_flag_choices... OK
web_1          |   Applying contenttypes.0002_remove_content_type_name... OK
web_1          |   Applying auth.0002_alter_permission_name_max_length... OK
web_1          |   Applying auth.0003_alter_user_email_max_length... OK
web_1          |   Applying auth.0004_alter_user_username_opts... OK
web_1          |   Applying auth.0005_alter_user_last_login_null... OK
web_1          |   Applying auth.0006_require_contenttypes_0002... OK
web_1          |   Applying auth.0007_alter_validators_add_error_messages... OK
web_1          |   Applying auth.0008_alter_user_username_max_length... OK
web_1          |   Applying auth.0009_alter_user_last_name_max_length... OK
web_1          |   Applying auth.0010_alter_group_name_max_length... OK
web_1          |   Applying auth.0011_update_proxy_permissions... OK
web_1          |   Applying sessions.0001_initial... OK
web_1          |   Applying unlocode.0001_initial... OK
web_1          | Saved downloaded resource at /tmp/tmp1uxv92c8/loc192csv.zip
web_1          | Extracted CSV files: ['2019-2 UNLOCODE CodeListPart3.csv', '2019-2 UNLOCODE CodeListPart1.csv', '2019-2 UNLOCODE CodeListPart2.csv']
web_1          | Created 111178 fixtures for model 'unlocode.unlocode'
web_1          | Saved fixture in unlocode/fixtures/unlocode_20200615_214220.json
web_1          | Installing fixture from unlocode/fixtures/unlocode_20200615_214220.json...
web_1          | Loading 'unlocode/fixtures/unlocode_20200615_214220' fixtures...
web_1          | Checking '/code/unlocode/fixtures/unlocode/fixtures' for fixtures...
web_1          | No fixture 'unlocode_20200615_214220' in '/code/unlocode/fixtures/unlocode/fixtures'.
web_1          | Checking '/code/unlocode/fixtures' for fixtures...
web_1          | Installing json fixture 'unlocode_20200615_214220' from '/code/unlocode/fixtures'.
Processed 111178 object(s).
web_1          | Resetting sequences
web_1          | Installed 111178 object(s) from 1 fixture(s)
web_1          | Watching for file changes with StatReloader
web_1          | Performing system checks...
web_1          |
web_1          | System check identified no issues (0 silenced).
web_1          | June 15, 2020 - 19:44:45
web_1          | Django version 3.0.7, using settings 'djangoprj.settings'
web_1          | Starting development server at http://0.0.0.0:8000/
web_1          | Quit the server with CONTROL-C.
```

Then you can check the number of entries in `unlocode` table:
```bash
docker exec -it unlocode_db_1 psql --username locode --dbname unlocode -c 'SELECT COUNT(*) FROM unlocode_unlocode;'
 count
--------
 111178
(1 row)
```
Now you can use the REST API to retrieve UN/LOCODE locations.

## 2. Create a REST API using Django REST Framework
### 2.1. Retrieve a single location by its LOCODE code
Return one instance, so this will work if there is only one instance with given code in the database.
```
GET http://localhost:8000/api/code/PL WAW/
{
    "id": 81342,
    "ch": "",
    "locode": "PL WAW",
    "name": "Warszawa",
    "namewodiacritics": "Warszawa",
    "subdiv": "14",
    "functions": [
        "2",
        "3",
        "4"
    ],
    "status": "AI",
    "date": "1307",
    "iata": "",
    "coordinates": "5215N 02100E",
    "remarks": ""
}
```
### 2.2. Retrieve a single location by its name without diacritics
Return one instance, so this will work if there is only one instance with given name in the database.
```
GET localhost:8000/api/name/Bydgoszcz/
{
    "id": 79761,
    "ch": "",
    "locode": "PL BZG",
    "name": "Bydgoszcz",
    "namewodiacritics": "Bydgoszcz",
    "subdiv": "",
    "functions": [
        "1",
        "2",
        "3",
        "4"
    ],
    "status": "AI",
    "date": "0307",
    "iata": "",
    "coordinates": "5309N 01800E",
    "remarks": ""
}
```
### 2.3. Using Django filters
Use `django-filter` package to retrieve all the locations according to the value of given field. The resulting list of locations is the value of `"results"` key.
```
GET localhost:8000/api/?locode=BE BRU
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 5345,
            "ch": "",
            "locode": "BE BRU",
            "name": "Brussel (Bruxelles)",
            "namewodiacritics": "Brussel (Bruxelles)",
            "subdiv": "BRU",
            "functions": [
                "1",
                "2",
                "3",
                "4"
            ],
            "status": "AI",
            "date": "1101",
            "iata": "",
            "coordinates": "5050N 00420E",
            "remarks": ""
        },
        {
            "id": 5346,
            "ch": "",
            "locode": "BE BRU",
            "name": "Bruxelles (Brussel)",
            "namewodiacritics": "Bruxelles (Brussel)",
            "subdiv": "BRU",
            "functions": [
                "1",
                "2",
                "3",
                "4"
            ],
            "status": "AI",
            "date": "1101",
            "iata": "",
            "coordinates": "5050N 00420E",
            "remarks": ""
        }
    ]
}
```
```
GET localhost:8000/api/?namewodiacritics=Warszawa
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 81342,
            "ch": "",
            "locode": "PL WAW",
            "name": "Warszawa",
            "namewodiacritics": "Warszawa",
            "subdiv": "14",
            "functions": [
                "2",
                "3",
                "4"
            ],
            "status": "AI",
            "date": "1307",
            "iata": "",
            "coordinates": "5215N 02100E",
            "remarks": ""
        }
    ]
}
```
## 3. Check once a day if LOCODE database was updated
A `celery` task is set to download the resource from `http://www.unece.org/fileadmin/DAM/cefact/locode/loc192csv.zip` and install a fixture to the `Unlocode` table of the database automatically every day at 2AM (`Europe/Warsaw` timezone).

TODO: Perform import only when necessary, that is when the `last-modified` attribute in the header of the get request's response is newer than the date of the latest import.
