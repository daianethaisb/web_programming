from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name
    
class Auction(models.Model):
    title = models.CharField(max_length=40)
    description = models.CharField(max_length=120) 
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    price = models.DecimalField(max_digits=11, decimal_places=2)                            
    imageUrl = models.CharField(max_length=600)         
    isActive = models.BooleanField(default=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userAuction") 
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="buyerAuction") 
    buy_date= models.DateTimeField(null=True, auto_now=True) 
    auction_date = models.DateTimeField(null=True, auto_now_add=True)       

class Bid(models.Model):
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userBid")    
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, blank=True, null=True, related_name="auctionBid") 
    bid_date = models.DateTimeField(null=True, auto_now=True)          
    
    def __str__(self):
        return f"{self.user} bid {self.bid} $ on {self.auction}"

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userComment")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, blank=True, null=True, related_name="auctionComment")
    comment = models.CharField(max_length=200)       
    comment_date = models.DateTimeField(null=True, auto_now=True)

    def __str__(self):
        return f"{self.author} comment on {self.auction} - {self.comment_date}"

class Watchlist(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")