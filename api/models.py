from django.contrib.auth import get_user_model
from django.db import models

from recipes.models import Recipe

User = get_user_model()


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='userfav'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favrecipe'
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='api_follower')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='api_following')

    class Meta:
        unique_together = ['user', 'following']
