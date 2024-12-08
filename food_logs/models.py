from django.db import models
from django.conf import settings


class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., grams, ml, cups
    unit_type = models.CharField(
        max_length=20,
        choices=[
            ('weight', 'Weight'),
            ('volume', 'Volume'),
            ('count', 'Count'),
            ('special', 'Special'),
        ],
        default='count',
    )  # Categorize units (weight, volume, etc.)

    def __str__(self):
        return self.name


class FoodLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Associate log with a user
    food_name = models.CharField(max_length=255)  # e.g., Oatmeal, Orange Juice
    quantity = models.FloatField()  # e.g., 1.5
    unit = models.ForeignKey(Unit, on_delete=models.DO_NOTHING)  # e.g., grams, ml
    calories = models.FloatField(default=0)  # Calories (kcal)
    fat = models.FloatField(default=0)  # Fat (grams)
    carbs = models.FloatField(default=0)  # Carbohydrates (grams)
    sugar = models.FloatField(default=0)  # Sugar (grams)
    fiber = models.FloatField(default=0)  # Fiber (grams)
    protein = models.FloatField(default=0)  # Protein (grams)
    sodium = models.FloatField(default=0)  # Sodium (mg)
    log_date = models.DateTimeField(auto_now_add=True)  # Automatically add the timestamp

    def __str__(self):
        return f"{self.food_name} ({self.quantity} {self.unit.name})"