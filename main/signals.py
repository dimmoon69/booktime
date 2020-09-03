from io import BytesIO
import logging
from PIL import Image
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import ProductImage

THUMBNAIL_SIZE = (150, 150)
logger = logging.getLogger(__name__)


@receiver(pre_save, sender=ProductImage)
def generate_thumbnail(sender, instance, **kwargs):
    logger.info("Генерация миниатюр для продукта %d", instance.product.id)

    image = Image.open(instance.image)
    image = image.convert("RGB")
    image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
    temp_thumb = BytesIO()
    image.save(temp_thumb, "JPEG")
    temp_thumb.seek(0)

    # set save=False, в противном случае он будет работать в бесконечном цикле
    instance.thumbnail.save(instance.image.name, ContentFile(temp_thumb.read()), save=False)
    temp_thumb.close()