from django.test import TestCase
from django.urls import reverse
from main import forms


class TestPage(TestCase):
    """Тестирование страниц"""

    def test_home_page_works(self):
        """Тест страницы home"""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'BookTime')

    def test_about_us_page_works(self):
        """Тест страницы about_us"""
        response = self.client.get(reverse("about_us"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about_us.html')
        self.assertContains(response, 'BookTime')

    def test_contact_us_page_works(self):
        """Тест страницы contact_us"""
        response = self.client.get(reverse("contact_us"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact_form.html')
        self.assertContains(response, 'BookTime')
        self.assertIsInstance(response.context["form"], forms.ContactForm)