from django.urls import path
from . import views
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("<int:item_id>", views.page, name="item"),
    path("category/<int:category_id>", views.category, name="category"),
    path("<int:item_id>/edit", views.edit, name="edit"),
    path("<int:item_id>/bid", views.bid, name="bid"),
    path("<int:item_id>/comment", views.comment, name="comment"),
    path("<int:item_id>/opencloselisting", views.opencloselisting, name="opencloselisting"),   
    path("<int:item_id>/addtowishlist", views.addtowishlist, name="addtowishlist"),
    ]