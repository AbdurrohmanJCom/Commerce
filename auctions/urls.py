from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # listings info
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:id>", views.listing_detail, name="listing_detail"),

    # diactivate
    path("listing/<int:id>/close", views.close_listing, name="close_listing"),

    path('listing/<int:id>/bids', views.bids_for_listing, name='bids_for_listing'),

    # personal_account
    path('user_activities', views.user_activities, name='user_activities'),

    # watchlist
    path('listing<int:product_id>/add_to_favorites', views.add_to_favorites, name='add_to_favorites'),
    path('listing<int:product_id>/remove_from_favorites', views.remove_from_favorites, name='remove_from_favorites'),
    path('watchlist<int:id>', views.watchlist, name='watchlist'),

    # category
    path('categories', views.categories, name='categories'),
    path('categories/<int:id>', views.category_view, name='category'),
]
