import logging

from ckeditor_uploader.fields import RichTextUploadingField
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import (AbstractUser,
                                        BaseUserManager,
                                        )

from . import exceptions

logger = logging.getLogger(__name__)


class ProductTagManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class ProductTag(models.Model):
    """Тэг"""
    name = models.CharField('Название', max_length=32)
    slug = models.SlugField('URL', max_length=48)
    description = models.TextField('Описание', blank=True)
    active = models.BooleanField('Добавить', default=True)

    objects = ProductTagManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def natural_key(self):
        return self.slug


class ActiveManager(models.Manager):
    def active(self):
        return self.filter(active=True)


class Product(models.Model):
    """Товар"""
    tags = models.ManyToManyField(ProductTag, verbose_name='Тэг', blank=True)
    name = models.CharField('Название', max_length=32)
    description = RichTextUploadingField('Описание', blank=True)
    price = models.DecimalField('Стоимость', max_digits=6, decimal_places=2)
    slug = models.SlugField('URL', max_length=48)
    active = models.BooleanField('Добавить', default=True)
    in_stock = models.BooleanField('В наличии', default=True)
    date_updated = models.DateTimeField('Дата обновления', auto_now=True)

    objects = ActiveManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class ProductImage(models.Model):
    """Фото к товару"""
    product = models.ForeignKey(Product, verbose_name='Продукт', on_delete=models.CASCADE)
    image = models.ImageField('Фото товара', upload_to="product-images")
    thumbnail = models.ImageField('Миниатюра', upload_to="product-thumbnails", null=True)

    class Meta:
        verbose_name = "Фото товара"
        verbose_name_plural = "Фото товаров"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None

    email = models.EmailField('email address', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()


class Address(models.Model):
    """Адрес пользователя"""
    SUPPORTED_COUNTRIES = (
        ("uk", "Москва"),
        ("us", "Московская обл."),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField("Наименование адреса", max_length=60)
    address1 = models.CharField("Улица", max_length=60)
    address2 = models.CharField("Дом-кв/оф", max_length=60, blank=True)
    zip_code = models.CharField("Индекс", max_length=12, blank=True)
    city = models.CharField("Город", max_length=60)
    country = models.CharField("Регион", max_length=3, choices=SUPPORTED_COUNTRIES)

    def __str__(self):
        return ", ".join([self.name, self.address1, self.address2, self.zip_code, self.city, self.country])


class Basket(models.Model):
    """Корзина"""
    OPEN = 10
    SUBMITTED = 20
    STATUSES = ((OPEN, "Не оформленный"), (SUBMITTED, "Оформленный"))

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    status = models.IntegerField(choices=STATUSES, default=OPEN)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def is_empty(self):
        return self.basketline_set.all().count() == 0

    def count(self):
        return sum(i.quantity for i in self.basketline_set.all())

    def create_order(self, billing_address, shipping_address):
        if not self.user:
            raise exceptions.BasketException("Cannot create order without user")

        logger.info(
            "Creating order for basket_id=%d"
            ", shipping_address_id=%d, billing_address_id=%d",
            self.id,
            shipping_address.id,
            billing_address.id,
        )

        order_data = {
            "user": self.user,
            "billing_name": billing_address.name,
            "billing_address1": billing_address.address1,
            "billing_address2": billing_address.address2,
            "billing_zip_code": billing_address.zip_code,
            "billing_city": billing_address.city,
            "billing_country": billing_address.country,
            "shipping_name": shipping_address.name,
            "shipping_address1": shipping_address.address1,
            "shipping_address2": shipping_address.address2,
            "shipping_zip_code": shipping_address.zip_code,
            "shipping_city": shipping_address.city,
            "shipping_country": shipping_address.country,
        }
        order = Order.objects.create(**order_data)
        c = 0
        for line in self.basketline_set.all():
            for item in range(line.quantity):
                order_line_data = {
                    "order": order,
                    "product": line.product,
                }
                order_line = OrderLine.objects.create(
                    **order_line_data
                )
                c += 1

        logger.info(
            "Created order with id=%d and lines_count=%d",
            order.id,
            c,
        )

        self.status = Basket.SUBMITTED
        self.save()
        return order


class BasketLine(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField("Количество:", default=1, validators=[MinValueValidator(1)])


class Order(models.Model):
    """Заказ"""
    NEW = 10
    PAID = 20
    DONE = 30
    STATUSES = ((NEW, "New"), (PAID, "Paid"), (DONE, "Done"))

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUSES, default=NEW)
    billing_name = models.CharField(max_length=60)
    billing_address1 = models.CharField(max_length=60)
    billing_address2 = models.CharField(max_length=60, blank=True)
    billing_zip_code = models.CharField(max_length=12)
    billing_city = models.CharField(max_length=60)
    billing_country = models.CharField(max_length=3)
    shipping_name = models.CharField(max_length=60)
    shipping_address1 = models.CharField(max_length=60)
    shipping_address2 = models.CharField(max_length=60, blank=True)
    shipping_zip_code = models.CharField(max_length=12)
    shipping_city = models.CharField(max_length=60)
    shipping_country = models.CharField(max_length=3)
    date_updated = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)


class OrderLine(models.Model):
    NEW = 10
    PROCESSING = 20
    SENT = 30
    CANCELLED = 40
    STATUSES = ((NEW, "New"), (PROCESSING, "Processing"), (SENT, "Sent"), (CANCELLED, "Cancelled"))
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    status = models.IntegerField(choices=STATUSES, default=NEW)



