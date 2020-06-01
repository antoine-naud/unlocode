import csv
import json
import os
import requests
import zipfile
from datetime import datetime
from pytz import timezone
import tempfile

from django.core.management.base import BaseCommand
from django.core import management
from django.core.management.commands import loaddata


class Command(BaseCommand):
    help = 'Create and install a fixture for Unlocode table after saving it in folder given as first argument.' \
        'Data is fetched from a CSV resource at URL given as second argument. Example:\n' \
        'manage.py create_install_fixture unlocode/fixtures http://www.unece.org/fileadmin/DAM/cefact/locode/loc192csv.zip'

    def add_arguments(self, parser):
        parser.add_argument('path_to_fixtures', type=str)
        parser.add_argument('url_to_csv_zip', type=str)

    def handle(self, *args, **options):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.create_install_fixture(temp_dir,
                                        options['path_to_fixtures'],
                                        options['url_to_csv_zip'])

    def download_and_extract(self, url, tmp_dir, chunk_size=128):
        content_type = requests.head(url).headers.get('content-type')
        if 'text' in content_type.lower() or 'html' in content_type.lower():
            self.stdout.write(f'Resource is not downloadable: {url}')
            return None
        resp = requests.get(url, stream=True)
        if resp.status_code != 200:
            self.stdout.write(f'Could not download resource at URL: {url}')
            return None
        file_path = os.path.join(tmp_dir, os.path.split(url)[1])  # zip file name
        with open(file_path, 'wb') as fd:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                fd.write(chunk)
        self.stdout.write(f'Saved downloaded resource at {file_path}')
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)
        csv_files = [f for f in os.listdir(tmp_dir) if f.endswith('.csv') and 'UNLOCODE' in f]
        self.stdout.write(f'Extracted CSV files: {csv_files}')
        return csv_files

    def write_to_json_file(self, content, file_path):
        try:
            with open(file_path, 'w') as json_file:
                json_file.write(json.dumps(content, indent=4, separators=(',', ': ')))
        except IOError:
            self.stdout.write(f'Cannot save fixtures to file {file_path}')

    def create_fixture(self, content, model):
        fixtures = list()
        for i, element in enumerate(content):
            fixture = dict()
            fixture['pk'] = i + 1
            fixture['model'] = model
            fixture['fields'] = element
            fixtures.append(fixture)
        self.stdout.write(f"Created {len(fixtures)} fixtures for model '{model}'")
        return fixtures

    def create_install_fixture(self, tmp_dir, fixt_dir, csv_url):
        if not os.path.exists(fixt_dir):
            self.stdout.write(f'Folder for fixtures does not exist: {fixt_dir}')
            return
        csv_filenames = self.download_and_extract(csv_url, tmp_dir)
        if not csv_filenames:
            return

        unlocodes = list()
        for filename in sorted(csv_filenames):
            with open(os.path.join(tmp_dir, filename), encoding='ISO-8859-1', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row[2]: # skip COUNTRY heading rows
                        unlocode = dict()
                        # Only fields Locode, NameWoDiacritics, Function are required to be imported
                        unlocode['ch'] = row[0]
                        unlocode['locode'] = ' '.join([row[1], row[2]])
                        unlocode['name'] = row[3]
                        unlocode['namewodiacritics'] = row[4]
                        unlocode['subdiv'] = row[5]
                        unlocode['functions'] = ','.join([c for c in row[6] if c != '-'])
                        unlocode['status'] = row[7]
                        unlocode['date'] = row[8]
                        unlocode['iata'] = row[9]
                        unlocode['coordinates'] = row[10]
                        unlocode['remarks'] = row[11]
                        unlocodes.append(unlocode)
        unlocode_fixtures = self.create_fixture(unlocodes, 'unlocode.unlocode')

        # Write all fixtures to a JSON file
        date_time = datetime.now(tz=timezone('Europe/Warsaw')).strftime('%Y%m%d_%H%M%S')
        fixt_file = os.path.join(fixt_dir, 'unlocode_{}.json'.format(date_time))
        self.write_to_json_file(unlocode_fixtures, fixt_file)
        self.stdout.write(f'Saved fixture in {fixt_file}')

        # Now load the fixture to the database
        self.stdout.write(f'Installing fixture from {fixt_file}...')
        management.call_command(loaddata.Command(), fixt_file, verbosity=3)
