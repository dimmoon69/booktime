from django import forms
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)


class ContactForm(forms.Form):
    """Форма обратной связи"""
    name = forms.CharField(label='Ваше имя', max_length=100)
    message = forms.CharField(label='Ваше сообщение', max_length=600, widget=forms.Textarea)

    def send_mail(self):
        logger.info("Отправка электронной почты в службу поддержки клиентов")
        message = "From: {0}\n{1}".format(self.cleaned_data["name"], self.cleaned_data["message"])
        send_mail("Сообщение с сайта", message, "site@booktime.domain", ["customerservice@booktime.domain"], fail_silently=False)