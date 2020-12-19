from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, unique=True, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)

    def __str__(self):
        return f'Profile for {self.user.first_name}'

# a many tomany model relationship for followed users and following users
class Contact(models.Model):
    # user that is following
    user_from = models.ForeignKey('auth.User', related_name='rel_from_set', on_delete=models.CASCADE)
    # user being followed
    user_to = models.ForeignKey('auth.User', related_name='rel_to_set', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'

# Ordinarily, this doesn't create any extra field in the user model
# the user model should be left untouched
# this practice is considered not ideal, instead create a custom user model if you need to edit the user model.
# Add the following field to the user model dynamically
user_model = get_user_model()
# set symmetrical to false so it won't automatically create a relation for the other party i.e
# if i follow you, it doesn't mean that you should follow me
user_model.add_to_class('following', models.ManyToManyField(
                                    'self', through=Contact,
                                    related_name='followers',
                                    symmetrical=False
                                ))
