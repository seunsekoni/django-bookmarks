from django.db import models
from django.conf import settings
from django.urls import reverse

from django.utils.text import slugify

# Create your models here.
class Image(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='images_created')
    title = models.CharField(max_length=200)
    slug = models.SlugField(blank=True, max_length=200)
    url = models.URLField()
    image = models.ImageField(upload_to='images/%Y/%m/%d/')
    description = models.TextField(blank=True)
    created = models.DateField(auto_now_add=True, db_index=True)
    users_like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='images_liked', blank=True)
    # add this field and use signals to update this field to avoid expensive queries which will deter performance
    # ordreing an annotaion query is expensive
    # updatethis field according to the total number of users_like in the manyToMany table
    total_likes = models.PositiveIntegerField(db_index=True, default=0)


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        '''
        Override the Image model save method to auto generate 
        slugs for each fields if an image slug wasn't provided
        '''
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        '''
            Override the get_absolute_url method of Image model
        '''
        return reverse('images:detail', args=[self.id, self.slug])