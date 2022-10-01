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
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=5)
    label = models.CharField(choices=LABEL_CHOICES, max_length=30)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(upload_to='items/%Y/%m/%d/', blank=True, default='images.jpeg')

    def __str__(self):
        return self.title

    def get_discount_percent(self):
        discount_percent = 100 - ((self.discount_price * 100) / self.price)
        return discount_percent
