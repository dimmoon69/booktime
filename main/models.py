from django.db import models


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


