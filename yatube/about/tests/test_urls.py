from http import HTTPStatus

from django.test import Client, TestCase


class AboutViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_about_status_code_200(self):
        pages = [
            '/about/author/',
            '/about/author/',
        ]
        for page in pages:
            with self.subTest(page=page):
                response = AboutViewsTests.client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)
