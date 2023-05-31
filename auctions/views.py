from decimal import Decimal
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max

from .models import *


def index(request):
    active_listings = Listing.objects.filter(is_active=True)

    return render(request, "auctions/index.html", {
        'listings': active_listings
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
        birth_date = request.POST["birth_date"]

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
            user.birth_date = birth_date
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


class ListingForm(forms.Form):
    title = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    imageUrl = forms.CharField(max_length=1000, widget=forms.TextInput(attrs={'class': 'form-control'}))
    initial_bid = forms.DecimalField(max_digits=11, decimal_places=2,
                                     widget=forms.TextInput(attrs={'class': 'form-control'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all().order_by('title'),
                                      widget=forms.Select(attrs={'class': 'form-control'}))


def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)

        if form.is_valid():
            Listing(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                category=form.cleaned_data['category'],
                price=form.cleaned_data['initial_bid'],
                owner=request.user,
                image_url=form.cleaned_data['imageUrl']
            ).save()
            return HttpResponse('Listing created')

        return HttpResponse('Form data is not valid')

    return render(request, 'auctions/create_listing.html', {
        'form': ListingForm()
    })


def listing_detail(request, id):
    listing = Listing.objects.get(id=id)
    last_bid = listing.bids.last()
    is_current_bidder = False

    if last_bid is not None:
        is_current_bidder = last_bid.bidder == request.user

    message = ''
    max_bid = listing.bids.aggregate(amount_max=Max('amount'))['amount_max']
    if max_bid is not None:
        min_bid_amount = max_bid + 10
    else:
        min_bid_amount = listing.price

    if request.method == 'POST':
        bid_amount = Decimal(request.POST['bid_amount'])

        print(bid_amount)
        print(min_bid_amount)

        print(bid_amount.__class__.__name__)
        print(min_bid_amount.__class__.__name__)

        print(min_bid_amount == bid_amount)

        if bid_amount < min_bid_amount:
            message = f'Min bid amount is {min_bid_amount}'
        else:
            Bid(
                listing=listing,
                bidder=request.user,
                amount=bid_amount
            ).save()

    return render(request, 'auctions/listing_detail.html', {
        'listing': listing,
        'bids_len': len(listing.bids.all()),
        'max_bid': max_bid,
        'min_bid_amount': min_bid_amount,
        'message': message,
        'is_current_bidder': is_current_bidder
    })


def bids_for_listing(request, id):
    return render(request, 'auctions/bids_for_listing.html', {
        'listing': Listing.objects.get(id=id)
    })


def close_listing(request, id):
    listing = Listing.objects.get(id=id)
    listing.is_active = False
    listing.save()

    return HttpResponseRedirect(reverse('listing_detail', kwargs={'id': id}))


def user_activities(request):
    listing = Listing.objects.all()

    return render(request, 'auctions/user_activities.html', {
        'listings': listing
    })
