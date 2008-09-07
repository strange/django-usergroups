from django.db import models
from django.contrib.auth.models import User

class Organization(models.Model):
    name = models.CharField(max_length=130)

    admins = models.ManyToManyField(User, related_name='admins')
    
    lines_of_work = models.ManyToManyField('Category')
    
    info = models.TextField(blank=True)
    website = models.URLField(blank=True)
    featured = models.BooleanField(default=False)


class Category(models.Model):
    title = models.CharField(max_length=30)
    slug = models.SlugField()
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        ordering = ('title',)
        verbose_name_plural = 'categories'