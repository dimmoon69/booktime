from django.test import TestCase
from main import models
from decimal import Decimal


class TestModel(TestCase):
    """Тест модели Product"""
    def test_active_manager_works(self):
        models.Product.objects.create(name="The cathedral and the bazaar", price=Decimal("10.00"))
        models.Product.objects.create(name="Pride and Prejudice", price=Decimal("2.00"))
        models.Product.objects.create(name="A Tale of Two Cities", price=Decimal("2.00"), active=False)
        self.assertEqual(len(models.Product.objects.active()), 2)