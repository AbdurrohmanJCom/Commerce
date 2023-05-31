from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    birth_date = models.DateField(auto_now_add=True)
    watchlist = models.ManyToManyField('auctions.Listing', related_name='watchers')

    def __str__(self):
        return self.username


class Category(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Catagories'


class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(Category, related_name='listings', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    owner = models.ForeignKey(User, related_name='listings', on_delete=models.CASCADE)
    image_url = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.title


class Bid(models.Model):
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    listing = models.ForeignKey(Listing, related_name='bids', on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, related_name='bids', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.bidder} -> {self.listing} -> {self.amount}'


class Comment(models.Model):
    owner = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.owner} -> {self.listing}'
