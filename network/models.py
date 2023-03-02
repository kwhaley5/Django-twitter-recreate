from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    picture = models.URLField(max_length=512, null=True, blank=True)
    pass

#I need to keep track of posts, followers, and likes
class Post(models.Model):
    post = models.CharField(max_length=255)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='User')
    likes = models.IntegerField(default=0)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} tweeted '{self.post}'"
    
    def serialize(self):
        return {
            "id": self.id,
            "post": self.post,
            "likes": self.likes,
            "timestamp": self.time
        }
    
class Following(models.Model):
    current_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    followed_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")

    def __str__(self):
        return f"{self.current_user_id} followed {self.followed_user_id}"
    
class Likes(models.Model):
    user_liked = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Likes")
    liked_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likedPost")

    def __str__(self):
        return f"{self.user_liked} liked {self.liked_post}"
    
    def keep (self):
        return {
            "id": self.id,
            "likes": self.user_liked,
            "liked": self.liked_post
        }
