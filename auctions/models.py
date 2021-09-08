from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE

class User(AbstractUser):
    pass
    def __str__(self):
        return f"{self.username}"


class Category(models.Model):
    category = models.CharField(max_length=64)
    def __str__(self):
        return self.category

class Listing(models.Model):
    owner = models.ForeignKey(User,on_delete=CASCADE,related_name="owner")
    title = models.CharField(max_length=64)
    description = models.TextField()
    price = models.IntegerField()
    winner = models.ForeignKey(User,on_delete=CASCADE,related_name="winner",blank=True,null=True)
    category = models.ManyToManyField(Category, related_name="categories")
    initial_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now=True)
    link = models.CharField(max_length=64,default=None,blank=True,null=True)
    image = models.FileField(null=True,blank=True,upload_to="images/")
    followed = models.ManyToManyField(User,blank = True,  related_name="following")
    active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.owner}({self.title})"


class Bid(models.Model):
    location = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="locationforbid")
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="userforbid", null=True,blank=True)
    bid = models.IntegerField()
    is_this_a_winning_bid = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user} bid {self.bid}$ in {self.location}"


class Comment(models.Model):
    location = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="locationforcomment")
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="userforcomment", null=True,blank=True)
    comment = models.TextField()
    def __str__(self):
        return f"{self.user} comment in {self.location}"