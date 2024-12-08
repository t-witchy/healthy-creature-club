from django.contrib import admin
from .models import FoodLog, Unit


@admin.register(FoodLog)
class FoodLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'food_name', 'quantity', 'unit', 'calories', 'log_date')
    list_filter = ('log_date', 'user')
    search_fields = ('food_name',)

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
