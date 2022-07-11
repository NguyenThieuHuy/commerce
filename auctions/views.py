from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, request
from django.http.response import HttpResponseServerError
from django.shortcuts import render,redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from .models import User,Bid,Comment,Listing,Category


def index(request):
    user = request.user
    items=Listing.objects.all()
    return render(request, "auctions/index.html",{
        "items":items,
        "categories":Category.objects.all(),
        "numsWish": Listing.objects.filter(followed=user.id).count(),
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
                "message": "Invalid username and/or password.",
            })
    else:
        return render(request, "auctions/login.html",{
            "categories":Category.objects.all()
        })


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
                "message": "Passwords must match.",
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken.",
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html",{
            "categories":Category.objects.all()
        })


def create(request):
    user = request.user
    if user.id is None:
        return render(request, "auctions/login.html",{
            "message": "Please Login to Create."
        })
    if request.method == "POST":
        listing = Listing()
        listing.owner = user
        listing.title = request.POST["Title"]
        listing.description = request.POST["Description"]
        listing.price = request.POST["Price"]
        listing.link = request.POST["link"]
        listing.save()
        category = Category.objects.filter(pk__in=(request.POST.getlist("Category")))
        for ca in category:
            ca.categories.add(listing)
        return HttpResponseRedirect(reverse("item",args=(listing.id,)))
    return render(request,"auctions/create.html",{
        "category": Category.objects.all(),
        "categories":Category.objects.all()
    })

def edit(request,item_id):
    try:
        item=Listing.objects.get(pk=item_id)
        if item.owner == request.user:
            if request.method == "POST":
                item.title = request.POST["Title"]
                item.description = request.POST["Description"]
                item.price = request.POST["Price"]
                if request.POST["link"] is not None:
                    item.link = request.POST["link"]
                else:item.link = None
                item.save()
                return HttpResponseRedirect(reverse("item",args=(item.id,)))
            return render(request,"auctions/edit.html",{
            "item":item,
            "category": Category.objects.all(),
            "categories":Category.objects.all()
            })
        else:
            return render(request,"auctions/index.html",{
            "message":"You do not have the authority to edit this page!!!!!"
        })
    except ObjectDoesNotExist:
            return render(request,"auctions/index.html",{
            "message":"No page found"
        })

def page(request,item_id):
    user = request.user
    item=Listing.objects.get(pk=item_id)
    comment=Comment.objects.filter(location=item)
    winner = item.winner
    return render(request, "auctions/listingpage.html",{
        "item":item,
        "user":user,
        "comments":comment,
        "winner":winner,
        "categories":Category.objects.all(),
        "numsWish": Listing.objects.filter(followed=user.id).count(),
    })

def bid(request,item_id):
    item=Listing.objects.get(pk=item_id)
    user = request.user
    if request.method == "POST":
        if user.id is not None:
            if int(request.POST["bid"]) > item.price:
                bid = Bid()
                bid.location = item
                bid.user = user
                bid.bid = request.POST["bid"]
                bid.save()
                item.price = request.POST["bid"]
                item.save()
                followed = User.objects.filter(pk=user.id)
                for f in followed:
                    f.following.add(item)
                return HttpResponseRedirect(reverse("item",args=(item_id,)))
            else:
                messages.info(request, 'Your bid must be greater than the current price!')
                return HttpResponseRedirect(reverse("item",args=(item_id,)))
        else:
            messages.info(request, 'You must login to bid!')
            return HttpResponseRedirect(reverse("item",args=(item_id,)))
    pass

def comment(request,item_id):
    item=Listing.objects.get(pk=item_id)
    user = request.user
    if request.method == "POST":
        if user.id is not None:
            comment = Comment()
            comment.location = item
            comment.user = user
            comment.comment = request.POST["comment"]
            comment.save()
            return HttpResponseRedirect(reverse("item",args=(item_id,)))
        else:
            messages.info(request, 'You must login to comment!')
            return HttpResponseRedirect(reverse("item",args=(item_id,)))
    pass

def category(request, category_id):
    user = request.user
    category = Category.objects.get(id=category_id)
    return render(request,"auctions/category.html",{
        "category": category,
        "listings": category.categories.all(),
        "categories":Category.objects.all(),
        "numsWish": Listing.objects.filter(followed=user.id).count(),
    })

def opencloselisting(request,item_id):
    item=Listing.objects.get(pk=item_id)
    user = request.user
    if request.method == "POST":
        if user == item.owner:
            #_______Winner_______#
            if item.active == True:
                bid = Bid.objects.filter(location=item)
                for b in bid:
                    if b.bid == item.price:
                        b.is_this_a_winning_bid = True
                        b.save()
                        item.winner = b.user
                        item.save()
                    else:
                        b.is_this_a_winning_bid = False
                        b.save()
            else:
                bid = Bid.objects.filter(location=item)
                for b in bid:
                    b.is_this_a_winning_bid = False
                    b.save()
            #_______________#
            if item.active == True:
                item.active = False
                item.save()
                return HttpResponseRedirect(reverse("item",args=(item_id,)))
            else: 
                item.active = True
                item.save()
                return HttpResponseRedirect(reverse("item",args=(item_id,)))
        else:
            messages.info(request, 'You do not have the authority to edit this page!!!!!')
            return HttpResponseRedirect(reverse("item",args=(item_id,)))

    pass


def wishlist(request):
    user = request.user
    item = Listing.objects.filter(followed=user.id)
    return render(request,"auctions/wishlist.html",{
    "user" : user,
    "item":item,
    "categories":Category.objects.all(),
    "numsWish": Listing.objects.filter(followed=user.id).count(),
    })

def addtowishlist(request,item_id):
    item=Listing.objects.get(pk=item_id)
    user = request.user
    if request.method == "POST":
        followed = User.objects.filter(pk=user.id)
        for f in followed:
            f.following.add(item)
        return HttpResponseRedirect(reverse("item",args=(item_id,)))
    pass
