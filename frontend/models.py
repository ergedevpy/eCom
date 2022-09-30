from django.db import models

CATEGORY_CHOICES = (
    ('C', 'Computer'),
    ('M', 'Mobile'),
    ('T', 'Tablet'),
)

LABEL_CHOICES = (
    ('N', 'New'),
    ('R', 'Refurbished'),
    ('U', 'Used'),

)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount = models.FloatField()
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=5)
    label = models.CharField(choices=LABEL_CHOICES, max_length=30)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(upload_to='items/%Y/%m/%d/', blank=True)

    def __str__(self):
        return self.title
