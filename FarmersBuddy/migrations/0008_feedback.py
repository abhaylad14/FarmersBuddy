# Generated by Django 3.2.6 on 2021-10-25 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FarmersBuddy', '0007_blog'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('Title', models.TextField(max_length=100)),
                ('Desc', models.TextField()),
                ('Date', models.DateField(auto_now_add=True)),
            ],
        ),
    ]