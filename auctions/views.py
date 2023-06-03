from decimal import Decimal
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
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
    comments = Comment.objects.filter(listing_id=id)
    listing = Listing.objects.get(id=id)
    max_bid = listing.bids.aggregate(max_price=Max("amount"))['max_price']
    last_bid = listing.bids.last()
    is_current_bidder = False
    if last_bid is not None:
        is_current_bidder = last_bid.bidder == request.user
    if max_bid is not None:
        min_bid_amount = max_bid + 10
    else:
        min_bid_amount = listing.price
    message = ''
    if request.method == 'POST':
        if request.POST.get('bid_amount'):
            bid_amount = Decimal(request.POST['bid_amount'])
            if bid_amount < min_bid_amount:
                message = f'Min bid amount is {round(min_bid_amount, 2)}'
            else:
                Bid(
                    listing=listing,
                    bidder=request.user,
                    amount=bid_amount
                ).save()
        if request.POST.get('comment'):
            Comment(
                owner=request.user,
                listing=listing,
                text=request.POST['comment'],
            ).save()
    return render(request, 'auctions/listing_detail.html', {
        'listing': listing,
        'bids_len': len(listing.bids.all()),
        'comments': comments,
        'max_bid': max_bid,
        'min_bid_amount': min_bid_amount,
        'message': message,
        'is_current_bidder': is_current_bidder,
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
    # Получение всех листингов и ставок, связанных с пользователем
    listings = Listing.objects.filter(owner=request.user)
    bids = Bid.objects.filter(bidder=request.user)

    # Получение имен листингов
    listing_names = [listing.title for listing in listings]
    bidding_listing_names = [bid.listing.title for bid in bids]

    # Получение ставок пользователя
    user_bids = [bid.amount for bid in bids]

    return render(request, 'auctions/user_activities.html', {
        'listings': listings,
        'bids': bids,
        'listing_names': listing_names,
        'bidding_listing_names': bidding_listing_names,
        'user_bids': user_bids,
    })


def watchlist(request, id):
    user_watchlist = Favorite.objects.filter(user_id=id)
    current_page = Paginator(user_watchlist, 4)
    page_number = request.GET.get('page')
    page_obj = current_page.get_page(page_number)
    return render(request, 'auctions/watchlist.html', {
        'listings': page_obj,
    })


def add_to_favorites(request, product_id):
    product = Listing.objects.get(pk=product_id)
    Favorite.objects.get_or_create(user=request.user, product=product)
    return HttpResponseRedirect(reverse("index"))


def remove_from_favorites(request, product_id):
    product = Listing.objects.get(pk=product_id)
    Favorite.objects.filter(user=request.user, product=product).delete()
    return HttpResponseRedirect(reverse("watchlist", args=(request.user.id,)))


def categories(request):
    categories = Category.objects.all()
    return render(request, 'auctions/list_categories.html', {
        'categories': categories
    })


def category_view(request, id):
    category = Listing.objects.filter(category_id=id)
    current_page = Paginator(category, 4)
    page_number = request.GET.get('page')
    page_obj = current_page.get_page(page_number)
    return render(request, 'auctions/category.html', {
        'listings': page_obj,
    })



