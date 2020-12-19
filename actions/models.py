from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


# Create your models here.
class Action(models.Model):
    user = models.ForeignKey('auth.User', related_name='actions', db_index=True, on_delete=models.CASCADE)
    verb = models.CharField(max_length=255)
    # tagrget_ct i.e target contentype
    content_type = models.ForeignKey(ContentType, related_name='target_obj',blank=True, null=True, on_delete=models.CASCADE)
    # target_id i.e target model id. primary key of the targeted model
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    # the generic column is not created in the db, it just maps content_type and object_id together
    target = GenericForeignKey('content_type', 'object_id')
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created',)

