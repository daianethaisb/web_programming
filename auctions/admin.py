from django.contrib import admin
from .models import Category, Auction, Bid, Comment, User

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(Comment)