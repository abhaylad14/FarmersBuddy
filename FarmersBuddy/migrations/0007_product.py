# Generated by Django 3.2.6 on 2021-10-11 13:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FarmersBuddy', '0006_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Name', models.CharField(max_length=50)),
                ('Desc', models.TextField()),
                ('Image', models.ImageField(upload_to='')),
                ('Price', models.PositiveBigIntegerField()),
                ('Quantity', models.PositiveIntegerField()),
                ('Keywords', models.TextField(max_length=50)),
                ('ProductBrand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FarmersBuddy.brand')),
                ('ProductCat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FarmersBuddy.category')),
            ],
        ),
    ]