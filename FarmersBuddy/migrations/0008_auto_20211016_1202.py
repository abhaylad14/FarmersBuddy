# Generated by Django 3.2.6 on 2021-10-16 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FarmersBuddy', '0007_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='Status',
            field=models.CharField(default='1', max_length=1),
        ),
        migrations.AlterField(
            model_name='product',
            name='Image',
            field=models.ImageField(upload_to='FarmersBuddy/products/'),
        ),
    ]
