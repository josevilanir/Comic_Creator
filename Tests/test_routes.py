import os
import tempfile
import unittest
from unittest.mock import patch

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import main

class TestRoutes(unittest.TestCase):
    def setUp(self):
        # Temporary directory for manga library
        self.tmpdir = tempfile.TemporaryDirectory()
        main.BASE_COMICS = self.tmpdir.name
        main.THUMBNAILS = os.path.join(self.tmpdir.name, "thumbs")
        os.makedirs(main.THUMBNAILS, exist_ok=True)
        main.URLS_JSON = os.path.join(self.tmpdir.name, "urls.json")
        main.app.config['TESTING'] = True
        self.client = main.app.test_client()

    def tearDown(self):
        self.tmpdir.cleanup()

    @patch('main.baixar_capitulo_para_pdf')
    def test_download_route(self, mock_download):
        mock_download.return_value = os.path.join(self.tmpdir.name, 'capitulo_001.pdf')
        response = self.client.post('/', data={
            'acao': 'baixar_manual',
            'base_url': 'http://example.com/manga/capitulo-',
            'capitulo': '1'
        })
        self.assertEqual(response.status_code, 302)
        mock_download.assert_called_once()

    def test_list_library(self):
        os.makedirs(os.path.join(main.BASE_COMICS, 'Manga1'), exist_ok=True)
        os.makedirs(os.path.join(main.BASE_COMICS, 'Manga2'), exist_ok=True)
        response = self.client.get('/biblioteca')
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        self.assertIn('Manga1', data)
        self.assertIn('Manga2', data)

    def test_delete_chapter(self):
        manga_dir = os.path.join(main.BASE_COMICS, 'MangaDel')
        os.makedirs(manga_dir, exist_ok=True)
        pdf_path = os.path.join(manga_dir, 'capitulo_001.pdf')
        thumb_path = os.path.join(manga_dir, 'capitulo_001.jpg')
        with open(pdf_path, 'wb') as f:
            f.write(b'dummy')
        with open(thumb_path, 'wb') as f:
            f.write(b'img')
        response = self.client.delete('/excluir_capitulo/MangaDel/capitulo_001.pdf')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])
        self.assertFalse(os.path.exists(pdf_path))
        self.assertFalse(os.path.exists(thumb_path))

    def test_delete_manga(self):
        manga_dir = os.path.join(main.BASE_COMICS, 'MangaWhole')
        os.makedirs(manga_dir, exist_ok=True)
        with open(os.path.join(manga_dir, 'dummy.pdf'), 'wb') as f:
            f.write(b'1')
        response = self.client.delete('/excluir_manga/MangaWhole')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])
        self.assertFalse(os.path.exists(manga_dir))

if __name__ == '__main__':
    unittest.main()
