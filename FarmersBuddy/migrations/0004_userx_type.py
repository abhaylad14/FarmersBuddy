# Generated by Django 3.2.6 on 2021-09-06 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FarmersBuddy', '0003_auto_20210906_1258'),
    ]

    operations = [
        migrations.AddField(
            model_name='userx',
            name='Type',
            field=models.CharField(default='c', max_length=1),
        ),
    ]