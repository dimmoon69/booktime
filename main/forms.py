import logging

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import (UserCreationForm as DjangoUserCreationForm)
from django.contrib.auth.forms import UsernameField
from django.core.mail import send_mail
from django.forms import inlineformset_factory

from . import models, widgets

logger = logging.getLogger(__name__)


class ContactForm(forms.Form):
    """Форма обратной связи"""
    name = forms.CharField(label='Ваше имя', max_length=100)
    message = forms.CharField(label='Ваше сообщение', max_length=600, widget=forms.Textarea)

    def send_mail(self):
        logger.info("Отправка электронной почты в службу поддержки клиентов")
        message = "From: {0}\n{1}".format(self.cleaned_data["name"], self.cleaned_data["message"])
        send_mail("Сообщение с сайта", message, "site@booktime.domain", ["customerservice@booktime.domain"], fail_silently=False)


class UserCreationForm(DjangoUserCreationForm):
    """Регистрация пользователя и отправка email"""
    class Meta(DjangoUserCreationForm.Meta):
        model = models.User
        fields = ("email",)
        field_classes = {"email": UsernameField}

    def send_mail(self):
        logger.info("Отправка электронной почты для регистрации email=%s", self.cleaned_data["email"])

        message = "Welcome {}".format(self.cleaned_data["email"])
        send_mail("Welcome to BookTime", message, "site@booktime.domain", [self.cleaned_data["email"]], fail_silently=True)


class AuthenticationForm(forms.Form):
    """Форма входа"""
    email = forms.EmailField()
    password = forms.CharField(strip=False, widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user = authenticate(self.request, email=email, password=password)
        if self.user is None:
            raise forms.ValidationError("Проверьте введенный email и пароль.")

        logger.info("Аутентификация прошла успешно для email=%s", email)

        return self.cleaned_data

    def get_user(self):
        return self.user


BasketLineFormSet = inlineformset_factory(models.Basket, models.BasketLine, fields=("quantity",), extra=0, widgets={"quantity": widgets.PlusMinusNumberInput()},)