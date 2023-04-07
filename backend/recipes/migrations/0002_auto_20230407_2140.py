# Generated by Django 2.2.16 on 2023-04-07 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-pub_date',)},
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(to='recipes.Ingredient'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', to='recipes.Tag'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='amount',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.FloatField(),
        ),
    ]