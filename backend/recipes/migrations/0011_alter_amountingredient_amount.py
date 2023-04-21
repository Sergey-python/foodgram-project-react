# Generated by Django 3.2.18 on 2023-04-21 17:58

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_auto_20230415_0406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amountingredient',
            name='amount',
            field=models.FloatField(default=0, error_messages={'errors': 'Количество не может быть отрицательным!'}, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
