import hashlib
import os
import shutil

import pytest

import main


@pytest.fixture
def client():
    main.app.config['TESTING'] = True
    return main.app.test_client()


class TestClass:

    @staticmethod
    def setup():
        folders = os.listdir('store')
        for folder in folders:
            if os.path.isdir(f'store/{folder}'):
                shutil.rmtree(f'store/{folder}')

    def test_upload(self, client):
        """Testing successful file upload."""

        with open('tests/Lenna.png', 'rb') as file:
            response = client.post('/upload', data={
                'file': file,
            })

        assert response.status_code == 200

        with open('tests/Lenna.png', 'rb') as file:
            file_content = file.read()

        json_data = response.get_json()
        assert json_data['hash'] == hashlib.md5(file_content).hexdigest()

    def test_upload_no_file(self, client):
        """Testing file upload request without the file."""

        response = client.post('/upload')
        assert response.status_code == 400

    def test_delete(self, client):
        """Testing file delete."""

        with open('tests/Lenna.png', 'rb') as file:
            file_content = file.read()

        file_hash = hashlib.md5(file_content).hexdigest()
        os.mkdir(f'store/{file_hash[:2]}')

        with open(f'store/{file_hash[:2]}/{file_hash}', 'wb') as file:
            file.write(file_content)

        response = client.post('/delete', json={
            'hash': file_hash,
        })
        assert response.status_code == 200

        folders = os.listdir('store')
        assert file_hash[:2] not in folders

    def test_delete_no_hash(self, client):
        """Testing file delete with no parameters."""

        response = client.post('/delete')
        assert response.status_code == 400

    def test_delete_no_such_file(self, client):
        """Testing file delete that does not exist."""

        response = client.post('/delete', json={
            'hash': '1234567',
        })
        assert response.status_code == 404

    def test_download(self, client):
        """Testing file download."""

        with open('tests/Lenna.png', 'rb') as file:
            file_content = file.read()

        file_hash = hashlib.md5(file_content).hexdigest()
        os.mkdir(f'store/{file_hash[:2]}')

        with open(f'store/{file_hash[:2]}/{file_hash}', 'wb') as file:
            file.write(file_content)

        response = client.post('/download', json={
            'hash': file_hash,
        })
        assert response.status_code == 200
        response_data = response.get_data()
        assert response_data == file_content
        
    def test_download_no_hash(self, client):
        """Testing file download with no parameters."""

        response = client.post('/download')
        assert response.status_code == 400

    def test_download_no_such_file(self, client):
        """Testing file download that does not exist."""

        response = client.post('/download', json={
            'hash': '1234567',
        })
        assert response.status_code == 404
