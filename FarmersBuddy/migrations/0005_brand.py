# Generated by Django 3.2.6 on 2021-09-20 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FarmersBuddy', '0004_userx_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('BrandName', models.CharField(max_length=50)),
                ('Status', models.CharField(default='1', max_length=1)),
            ],
        ),
    ]
