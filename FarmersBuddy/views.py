from typing import Type
from django.shortcuts import render, redirect
import re
from .models import *
import hashlib, random, smtplib
from django.contrib import messages
from django.http import HttpResponse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.views.decorators.cache import never_cache

def sendemail(receiver, subject, msg):
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    sender = "ladaebs14@gmail.com"
    server.login(sender, "Abhay@123")
    # message = "From: FarmersBuddy <{}> \n To: {} \n Subject: {} \n\n {} ".format(sender,receiver,subject,msg) 
    message = MIMEMultipart()
    message['From'] = "FarmersBuddy <" + sender + ">"
    message['To'] = receiver
    message['Subject'] = subject
    message.attach(MIMEText(msg, 'plain'))
    try:
        server.sendmail(sender,receiver,message.as_string())
        print("Successfully sent email")
        server.quit()
    except smtplib.SMTPException:
        print("Error: unable to send email")

@never_cache
def index(request):
    return render(request,"FarmersBuddy/Home/index.html")

@never_cache
def verify(request):
    otp = request.session['otp']
    email = str(request.session['email'])
    sendemail(email, "Verify Account", "Your verification OTP is: " + str(otp))
    if request.method == "POST":
        txtotp = request.POST.get("txtotp","")
        if(txtotp != ""):
            if(txtotp == str(otp)):
                obj = Userx.objects.get(Email = email)
                obj.Status = "1"
                obj.save()
                request.session['id'] = obj.id
                return redirect(index)
            else:
                messages.error(request, "Invalid OTP")
        else:
            messages.error(request, "Empty from!")
    return render(request, "FarmersBuddy/Home/verify.html")

@never_cache
def logout(request):
    del request.session['id']
    if "admin" in request.session:
        del request.session['admin']
    return redirect(index)

@never_cache
def login(request):
    if request.method == "POST":
        txtemail = request.POST.get("txtemail","")
        txtpass = request.POST.get("txtpass","")
        print(txtemail, txtpass)
        if(txtemail != "" and txtpass != ""):
            pass1 = hashlib.sha256(txtpass.encode())
            check = Userx.objects.filter(Email = txtemail, Password = pass1.hexdigest(), Status = "1")
            if(len(check) == 1):
                obj = Userx.objects.get(Email = txtemail)
                request.session['id'] = obj.id
                if obj.Type == "c":
                    return redirect(index)
                elif obj.Type == "a":
                    request.session['admin'] = True
                    return redirect(admindashboard)
            else:
                check = Userx.objects.filter(Email = txtemail, Password = pass1.hexdigest(), Status = "2")
                if(len(check) == 1):
                    otp = random.randint(111111,999999)
                    request.session['otp'] = otp
                    request.session['email'] = txtemail
                    print(otp)
                    return redirect(verify)
                else:
                    messages.error(request, "Invalid Email or Password")
        else:
            messages.error(request, "Empty Form")
    if 'id' not in request.session:
        return render(request, "FarmersBuddy/Home/login.html")
    else:
        return redirect(index)

@never_cache
def registration(request):
    if request.method == "POST":
        flagfname = flaglname = flagmobile = flagaddress = flagemail = flagpass1 = flagpass1 = 0
        errstr = ""
        txtfname = request.POST.get("txtfname", "")
        txtlname = request.POST.get("txtlname","")
        txtmobile = request.POST.get("txtmobile","")
        txtaddress = request.POST.get("txtaddress","")
        txtemail = request.POST.get("txtemail","")
        txtpass1 = request.POST.get("txtpass1","")
        txtpass2 = request.POST.get("txtpass2","")
        
        if(txtfname != "" and txtlname != "" and txtmobile != "" and txtaddress != "" and txtemail != "" and 
        txtpass1 != "" and txtpass2 != ""):
            if(re.search("^[a-zA-Z]{2,20}$",txtfname)):
                flagfname = 1
            else:
                errstr += "Please enter valid Firstname\t"

            if(re.search("^[a-zA-Z]{2,20}$",txtlname)):
                flaglname = 1
            else:
                errstr += "Please enter valid Lastname\t"

            if(re.search("^[0-9]{10}$",txtmobile)):
                flagmobile = 1
            else:
                errstr += "Mobile number is not valid\t"

            if(re.search("^[a-zA-Z,-/ ,0-9]+$",txtaddress)):
                flagaddress = 1
            else:
                errstr += "Address is invalid"

            if(re.search("[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$",txtemail)):
                flagemail = 1
            else:
                errstr += "Please enter valid email\t"

            if(re.search("(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}",txtpass1)):
                flagpass1 = 1
            else:   
                errstr += "Please enter a valid password\t"

            if(flagfname == 1 and  flaglname == 1 and flagmobile == 1 and flagaddress == 1 and flagemail == 1 and flagpass1 == 1):
                if(txtpass1 == txtpass2):
                    exists = Userx.objects.filter(Email=txtemail)
                    if(len(exists) > 0):
                        messages.warning(request, "The User already exists!")
                    else:
                        pass1 = hashlib.sha256(txtpass1.encode())
                        newUser = Userx(FirstName = txtfname, LastName = txtlname, Email = txtemail, Password = pass1.hexdigest(), Mobile = txtmobile, Address1 = txtaddress)
                        newUser.save()
                        messages.success(request, "The User registered successfully!")
                else:
                    errstr += "Password and Re-Enter password does not match\t"
                    messages.error(request, errstr)
            else:
                messages.error(request, errstr)
        else:
            messages.error(request, "Invalid Request, Something went wrong!")
    return render(request,"FarmersBuddy/Home/registration.html")

# Admin Side
@never_cache
def admindashboard(request):
    return render(request, "FarmersBuddy/Admin/dashboard.html")

@never_cache
def customers(request):
    users = Userx.objects.filter(Type="c")
    print(users)
    dictusers = {
        "user": users
    }
    return render(request,"FarmersBuddy/Admin/customers.html", dictusers)

def changestatus(request):
    if request.method == "POST":
        sid = request.POST.get("id","")
        ustatus = request.POST.get("ustatus","")
        if(id != "" and ustatus != ""):
            if(ustatus == "0"):
                ustatus = 1
            else:
                ustatus = 0
            try:
                obj = Userx.objects.get(id=sid)
                obj.Status = ustatus
                obj.save()
                return HttpResponse("done")
            except:
                return HttpResponse("Invalid Request")
    else:
        return HttpResponse("Invalid Request")

def deletecustomer(request):
    if request.method == "POST":
        cid = request.POST.get("id","")
        print(cid)
        if(cid != ""):
            try:
                obj = Userx.objects.get(id=cid)
                obj.delete()
                return HttpResponse("done")
            except:
                return HttpResponse("Invalid Request")
    else:
        return HttpResponse("Invalid Request")

@never_cache
def managebrands(request):
    if request.method == "POST":
        txtbrand = request.POST.get("txtbrand","")
        if(txtbrand != ""):
            obj = Brand.objects.filter(BrandName=txtbrand)
            if(len(obj) > 0):
                messages.error(request, "Record already exists!")
            else:
                try:
                    brand = Brand(BrandName=txtbrand)
                    brand.save()
                    messages.success(request, "Brand added successfully!")
                except:
                    messages.error(request, "Something went wrong!")

    brands = Brand.objects.all()
    dictbrands = {
        "Brands": brands
    }
    return render(request, "FarmersBuddy/Admin/managebrands.html", dictbrands)

def changebrandstatus(request):
    if request.method == "POST":
        sid = request.POST.get("id","")
        ustatus = request.POST.get("ustatus","")
        if(id != "" and ustatus != ""):
            if(ustatus == "0"):
                ustatus = 1
            else:
                ustatus = 0
            try:
                obj = Brand.objects.get(id=sid)
                obj.Status = ustatus
                obj.save()
                return HttpResponse("done")
            except:
                return HttpResponse("Invalid Request")
    else:
        return HttpResponse("Invalid Request")

def deletebrand(request):
    if request.method == "POST":
        cid = request.POST.get("id","")
        print(cid)
        if(cid != ""):
            try:
                obj = Brand.objects.get(id=cid)
                obj.delete()
                return HttpResponse("done")
            except:
                return HttpResponse("Invalid Request")
    else:
        return HttpResponse("Invalid Request")

@never_cache
def managecategories(request):
    if request.method == "POST":
        # txtbrand = request.POST.get("txtbrand","")
        # if(txtbrand != ""):
        #     obj = Brand.objects.filter(BrandName=txtbrand)
        #     if(len(obj) > 0):
        #         messages.error(request, "Record already exists!")
        #     else:
        #         try:
        #             brand = Brand(BrandName=txtbrand)
        #             brand.save()
        #             messages.success(request, "Brand added successfully!")
        #         except:
        #             messages.error(request, "Something went wrong!")
        pass
    categories = Category.objects.all()
    dictbrands = {
        "Categories": categories
    }
    return render(request, "FarmersBuddy/Admin/managecategories.html", dictbrands)