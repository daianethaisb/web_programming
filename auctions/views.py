from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auction, Category, Watchlist, Bid, Comment

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["bid"]
        labels = { "bid": ("") }
        widgets = {
            "bid": forms.NumberInput(attrs={
                "placeholder": "Bid",
                "min": 0.01,
                "max": 100000000000,
                "class": "form-control"
            })
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]
        labels = {"comment": ("")}
        widgets = {
            "comment": forms.Textarea(attrs={
                "placeholder": "Comment here",
                "class": "form-control",
                "rows": 1
            })
        }


def index(request):
   return render(request, "auctions/index.html", {
        "auctions": Auction.objects.filter(isActive=True)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def createAuction(request):
    if request.method == "POST":
        auction = Auction()
        auction.title = request.POST.get("title")
        auction.description = request.POST.get("description") 
        auction.category = Category.objects.get(pk=int(request.POST["category"]))                          
        auction.imageUrl = request.POST.get("imageUrl")
        auction.price = request.POST.get("price")
        auction.seller= User.objects.get(id=request.user.id)    

        auction.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/createAuction.html", {
            "category": Category.objects.all()
        })
    
def viewAuction(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    comments = Comment.objects.filter(auction=auction_id)

    if request.user.is_authenticated:
            watchlist_item = Watchlist.objects.filter(
                    auction = auction_id,
                    user = User.objects.get(id=request.user.id)).first()

            if watchlist_item is not None:
                on_watchlist = True
            else:
                on_watchlist = False
    else:
        on_watchlist = False

    return render (request, "auctions/auction.html", {
        "auction": auction,
        "bid_form": BidForm(),
        "comment_form": CommentForm(),
        "on_watchlist": on_watchlist,
        "comments": comments
    }) 

def watchlist(request):

    if request.method == "POST":
        auction_id = request.POST.get("auction_id")

        try:
            auction = Auction.objects.get(pk=auction_id)
            user = User.objects.get(id=request.user.id)
        except Auction.DoesNotExist:
            return render(request, "auctions/errorPage.html", {
                "code": 404,
                "message": "Auction id doesn't exist"
            })

        if request.POST.get("on_watchlist") == "True":
            watchlist_item_to_delete = Watchlist.objects.filter(
                user = user,
                auction = auction
            )
            watchlist_item_to_delete.delete()
        else:
            watchlist_item = Watchlist(
                user = user,
                auction = auction
            )
            watchlist_item.save()

        return HttpResponseRedirect("viewAuction/" + auction_id)
    
    watchlist_auctions = User.objects.get(id=request.user.id).watchlist.values_list("auction")
    watchlist_items = Auction.objects.filter(id__in=watchlist_auctions, isActive=True)

    return render(request, "auctions/index.html", {
        "auctions": watchlist_items,
        "title": "Watchlist"
    })

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })

def categoryList(request, category_id):
    return render(request, "auctions/index.html", {
        "auctions": Auction.objects.filter(category=category_id, isActive=True),
        "titleCategory": Category.objects.get(pk=category_id)
    })

def bid(request):
    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            price_bid = float(form.cleaned_data["bid"])
            auction_id = request.POST.get("auction_id")

            try:
                auction = Auction.objects.get(pk=auction_id)
                user = User.objects.get(id=request.user.id)
            except Auction.DoesNotExist:
                return render(request, "auctions/errorPage.html", {
                    "code": 404,
                    "message": "Auction id doesn't exist"
                })

            current_bid = Bid.objects.filter(auction=auction).order_by('-bid').first()

            if current_bid is None:
                current_bidAucition = float(auction.price)
            else:
                current_bidAucition = current_bid.bid

            if request.user.is_authenticated:
                watchlist_item = Watchlist.objects.filter(
                        auction = auction_id,
                        user = User.objects.get(id=request.user.id)).first()

                if watchlist_item is not None:
                    on_watchlist = True
                else:
                    on_watchlist = False
            else:
                on_watchlist = False

            if price_bid > current_bidAucition:
                new_bid = Bid(auction=auction, user=user, bid=price_bid)
                new_bid.save()

                auction.price = price_bid
                auction.save()

                return render (request, "auctions/auction.html", {
                    "auction": auction,
                    "bid_form": BidForm(),
                    "comment_form": CommentForm(),
                    "comments": Comment.objects.filter(auction=auction_id),
                    "on_watchlist": on_watchlist,
                    "message": "Congratulations! You're winning this bidding war",
                    "statusMessage" : "success"
                }) 
            else:
               return render (request, "auctions/auction.html", {
                    "auction": auction,
                    "bid_form": BidForm(),
                    "comment_form": CommentForm(),
                    "comments": Comment.objects.filter(auction=auction_id),
                    "on_watchlist": on_watchlist,
                    "message": "The value of this bid is very low",
                    "statusMessage" : "error"
                }) 
               
        else:
            return render(request, "auctions/errorPage.html", {
                "code": 400,
                "message": "Form is invalid"
            })
        
    return render(request, "auctions/errorPage.html", {
        "code": 405,
        "message": "Method Not Allowed"
    })

def closeAuction(request, auction_id):
    
    if request.method == "POST":
        auction = Auction.objects.get(pk=auction_id)
        highest_bid = Bid.objects.filter(auction=auction).order_by('-bid').first()
        
        if Bid.objects.filter(auction=auction).order_by('-bid').first() is None:
            return render (request, "auctions/auction.html", {
                "auction": auction,
                "bid_form": BidForm(),
                "comment_form": CommentForm(),
                "comments": Comment.objects.filter(auction=auction_id),
                "message": "There are no bids for this auction yet.",
                "statusMessage" : "error"
            }) 
        else:
            auction.buyer = highest_bid.user
            auction.price = highest_bid.bid
            auction.isActive = False
            auction.save()
        
        return render (request, "auctions/auction.html", {
            "auction": auction,
            "bid_form": BidForm(),
            "comment_form": CommentForm(),
            "comments": Comment.objects.filter(auction=auction_id),
            "message": "Your auction has ended successfully.",
            "statusMessage" : "success"
        }) 

    elif request.method == "GET":
        return render(request, "auctions/errorPage.html", {
            "code": 405,
            "message": "Method Not Allowed"
        })

def comment(request, auction_id):
    
    if request.method == "POST":
        form = CommentForm(request.POST)
        auction = Auction.objects.get(pk=auction_id)

        if form.is_valid():
            comment = form.cleaned_data["comment"]
            comment = Comment(
                author=User.objects.get(pk=request.user.id),
                comment = comment,
                auction = auction
            )
            comment.save()

            if request.user.is_authenticated:
                watchlist_item = Watchlist.objects.filter(
                        auction = auction_id,
                        user = User.objects.get(id=request.user.id)).first()

                if watchlist_item is not None:
                    on_watchlist = True
                else:
                    on_watchlist = False
            else:
                on_watchlist = False

            return render (request, "auctions/auction.html", {
                "auction": auction,
                "bid_form": BidForm(),
                "comment_form": CommentForm(),
                "on_watchlist": on_watchlist,
                "comments": Comment.objects.filter(auction=auction_id)
            }) 
        else:
            return render(request, "auctions/errorPage.html", {
                "code": 400,
                "message": "Form is invalid"
            })
    elif request.method == "GET":
        return render(request, "auctions/errorPage.html", {
            "code": 405,
            "message": "Method Not Allowed"
        })
    