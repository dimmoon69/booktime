from django.test import TestCase
from django.core import mail
from main import forms


class TestForm(TestCase):
    """Тест форм"""

    def test_valid_contact_us_form_sends_email(self):
        """форма контактов"""
        form = forms.ContactForm({
            'name': "Дмитрий П",
            'message': "Привет"
        })
        self.assertTrue(form.is_valid())
        with self.assertLogs('main.forms', level='INFO') as cm: form.send_mail()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Сообщение с сайта')
        self.assertGreaterEqual(len(cm.output), 1)

    def test_invalid_contact_us_form(self):
        form = forms.ContactForm({
            'message': "Привет"
        })
        self.assertFalse(form.is_valid())

    def test_valid_signup_form_sends_email(self):
        """форма регистрации"""
        form = forms.UserCreationForm(
                {
                    "email": "user@domain.com",
                    "password1": "abcabcabc",
                    "password2": "abcabcabc",
                }
        )
        self.assertTrue(form.is_valid())
        with self.assertLogs("main.forms", level="INFO") as cm:
            form.send_mail()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Welcome to BookTime")
        self.assertGreaterEqual(len(cm.output), 1)