# Generated by Django 2.2.16 on 2023-04-15 00:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_auto_20230414_2313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopingcart',
            name='recipes',
            field=models.ManyToManyField(related_name='shopping_cart', to='recipes.Recipe'),
        ),
    ]
