# Generated by Django 4.2.7 on 2023-12-27 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('image', models.ImageField(upload_to='product_images/')),
                ('category', models.CharField(choices=[('pizza', 'Pizza'), ('burger', 'Burger'), ('drink', 'Drink')], default='pizza', max_length=10)),
            ],
        ),
    ]