from django.db import models
from django.contrib.auth.models import (AbstractUser,
                                        BaseUserManager,
                                        )


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

    def natural_key(self):
        return self.slug


class ActiveManager(models.Manager):
    def active(self):
        return self.filter(active=True)


class Product(models.Model):
    """Товар"""
    tags = models.ManyToManyField(ProductTag, verbose_name='Тэг', blank=True)
    name = models.CharField('Название', max_length=32)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Стоимость', max_digits=6, decimal_places=2)
    slug = models.SlugField('URL', max_length=48)
    active = models.BooleanField('Добавить', default=True)
    in_stock = models.BooleanField('В наличии', default=True)
    date_updated = models.DateTimeField('Дата обновления', auto_now=True)

    objects = ActiveManager()

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """Фото к товару"""
    product = models.ForeignKey(Product, verbose_name='Продукт', on_delete=models.CASCADE)
    image = models.ImageField('Фото товара', upload_to="product-images")
    thumbnail = models.ImageField('Миниатюра', upload_to="product-thumbnails", null=True)


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


