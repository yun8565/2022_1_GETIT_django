from django.contrib import admin
from .models import Category
from .models import Post

# Register your models here.
admin.site.register(Post)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug" : ('name',)}

admin.site.register(Category, CategoryAdmin)