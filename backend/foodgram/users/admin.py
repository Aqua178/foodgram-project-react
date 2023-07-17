from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'recipes_count',
        'subscribers_count',

    )
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email',)
    list_display_links = ('id', 'username', 'email',)

    @admin.display(description='Счетчик рецептов')
    def recipes_count(self, obj):
        return obj.recipes.all().count()

    @admin.display(description='Счетчик подписчиков')
    def subscribers_count(self, obj):
        return obj.following.all().count()


admin.site.unregister(Group)
