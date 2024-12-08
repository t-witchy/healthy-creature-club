# Generated by Django 5.1.4 on 2024-12-08 20:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('unit_type', models.CharField(choices=[('weight', 'Weight'), ('volume', 'Volume'), ('count', 'Count'), ('special', 'Special')], default='count', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='FoodLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food_name', models.CharField(max_length=255)),
                ('quantity', models.FloatField()),
                ('calories', models.FloatField(default=0)),
                ('fat', models.FloatField(default=0)),
                ('carbs', models.FloatField(default=0)),
                ('sugar', models.FloatField(default=0)),
                ('fiber', models.FloatField(default=0)),
                ('protein', models.FloatField(default=0)),
                ('sodium', models.FloatField(default=0)),
                ('log_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='food_logs.unit')),
            ],
        ),
    ]
