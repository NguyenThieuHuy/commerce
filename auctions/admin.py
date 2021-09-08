from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.admin.options import ModelAdmin
from .models import User,Bid,Comment,Listing,Category

#Register your models here.

class ListingAdmin(admin.ModelAdmin):
  filter_horizontal = ("category","followed",)

class ModelInline1(admin.TabularInline):
  model = Listing.category.through

class ModelInLine2(admin.TabularInline):
  model = Listing.followed.through

class CategoryAdmin(admin.ModelAdmin):
  inlines = [
      ModelInline1,
  ]

class UserAdmin(admin.ModelAdmin):
  inlines = [
    ModelInLine2,
  ]
# ________
admin.site.register(User,UserAdmin)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Listing,ListingAdmin)
admin.site.register(Category,CategoryAdmin)


