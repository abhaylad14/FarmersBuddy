from django.db import models
from django.core.validators import RegexValidator

# Create your models here.
Status_Choice = (("1", "Active"), ("0", "Inactive"))

class Userx(models.Model):
    id = models.AutoField(primary_key=True)
    FirstName = models.CharField(max_length=20)
    LastName = models.CharField(max_length=20)
    Email = models.EmailField(max_length=50)
    Password = models.CharField(max_length=64, editable=False)
    Mobile = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{10}$')])
    Address1 = models.TextField(max_length=100, verbose_name="Address")
    Address2 = models.TextField(blank=True,max_length=100, verbose_name="Alternative Address")
    Type = models.CharField(max_length=1, default="c")
    Status = models.CharField(
        max_length = 1,
        choices = Status_Choice,
        default = '2'
        )
    def __str__(self):
        return (self.FirstName + self.LastName)

class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    BrandName = models.CharField(max_length=50)
    Status = models.CharField(max_length=1, default="1")

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    CategoryName = models.CharField(max_length=50)
    Status = models.CharField(max_length=1, default="1")
