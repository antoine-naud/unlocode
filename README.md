
# Dockerized Django app with Postgres importing UN/LOCODE database

(inspired from https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/)

## 1. Setup the application
### 1.1. Download the repository
```bash
git clone https://github.com/antoine-naud/unlocode
cd unlocode
```

### 1.2. Build the images and spin up the two containers
```
docker-compose build
docker-compose up -d
```
The `web` container will perform initial migration, then it will execute initial import of data to `Unlocode` table in the database (the import takes about 2 minutes). After importing data, the Django server is started. You can check the logs at:
```
docker-compose logs web
...
web_1  | Django version 2.2.12, using settings 'djangoprj.settings'
web_1  | Starting development server at http://0.0.0.0:8000/
web_1  | Quit the server with CONTROL-C.
```

### 1.3. Run initial migration
```
docker-compose exec web python djangoprj/manage.py migrate --noinput
```

### 1.4. Import data to `unlocode` table
Data is imported to `unlocode` table by a custom Django command `create_install_fixture`. This command downloads data in zipped CSV files from given URL, creates a fixture and install it using `loaddata` Django command.
```bash
docker-compose exec web python djangoprj/manage.py create_install_fixture djangoprj/unlocode/fixtures http://www.unece.org/fileadmin/DAM/cefact/locode/loc192csv.zip
Saved downloaded resource at /tmp/tmpwzkhg8g6/loc192csv.zip
Extracted CSV files: ['2019-2 UNLOCODE CodeListPart3.csv', '2019-2 UNLOCODE CodeListPart1.csv', '2019-2 UNLOCODE CodeListPart2.csv']
Created 111178 fixtures for model 'unlocode.unlocode'
Saved fixture in djangoprj/unlocode/fixtures/unlocode_20200609_113920.json
Installing fixture from djangoprj/unlocode/fixtures/unlocode_20200609_113920.json
Processed 111178 object(s).
Resetting sequences
Installed 111178 object(s) from 1 fixture(s)
```

The execution time needed to import all 111178 items is ~90 seconds.

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
A `celery` task is set to download the resource from `http://www.unece.org/fileadmin/DAM/cefact/locode/loc192csv.zip` and install a fixture to the `Unlocode` table of the database automatically every day at 2AM.

TODO: Perform import only in case when the `last-modified` attribute in the header of the request's response is newer than the date of the latest import.
