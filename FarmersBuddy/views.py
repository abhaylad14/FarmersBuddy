from math import ceil
from typing import Type
from django.shortcuts import render, redirect
import re,razorpay
from .models import *
import hashlib, random, smtplib
from django.contrib import messages
from django.http import HttpResponse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.views.decorators.cache import never_cache

MAX_SIZE = 2*1024*1024
def valid_image_size(image, max_size=MAX_SIZE):
    width = image.size
    height = image.size
    if (width * height) > max_size:
        return (False, "Image is too large")
    return (True, image)

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

def updatebrand(request):
    if request.method == "POST":
        bid = request.POST.get("id","")
        ubrand = request.POST.get("ubrand","")
        print(bid)
        if(bid != "" and ubrand != ""):
            try:
                obj = Brand.objects.filter(BrandName=ubrand)
                if(len(obj) > 0):
                    return HttpResponse("Brand already exists")
                else:
                    obj = Brand.objects.get(id=bid)
                    obj.BrandName = ubrand
                    obj.save()
                    return HttpResponse("done")
            except:
                return HttpResponse("Something went wrong!")
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
        txtcategory = request.POST.get("txtcategory","")
        if(txtcategory != ""):
            obj = Category.objects.filter(CategoryName=txtcategory)
            if(len(obj) > 0):
                messages.error(request, "Record already exists!")
            else:
                try:
                    category = Category(CategoryName=txtcategory)
                    category.save()
                    messages.success(request, "Category added successfully!")
                except:
                    messages.error(request, "Something went wrong!")
        pass
    categories = Category.objects.all()
    dictbrands = {
        "Categories": categories
    }
    return render(request, "FarmersBuddy/Admin/managecategories.html", dictbrands)

def updatecategory(request):
    if request.method == "POST":
        cid = request.POST.get("id","")
        ucategory = request.POST.get("ucategory","")
        print(cid)
        if(cid != "" and ucategory != ""):
            try:
                obj = Category.objects.filter(CategoryName=ucategory)
                if(len(obj) > 0):
                    return HttpResponse("Category already exists")
                else:
                    obj = Category.objects.get(id=cid)
                    obj.CategoryName = ucategory
                    obj.save()
                    return HttpResponse("done")
            except:
                return HttpResponse("Something went wrong!")
    else:
        return HttpResponse("Invalid Request")

def deletecategory(request):
    if request.method == "POST":
        cid = request.POST.get("id","")
        print(cid)
        if(cid != ""):
            try:
                obj = Category.objects.get(id=cid)
                obj.delete()
                return HttpResponse("done")
            except:
                return HttpResponse("Invalid Request")
    else:
        return HttpResponse("Invalid Request")

def changecategorystatus(request):
    if request.method == "POST":
        sid = request.POST.get("id","")
        ustatus = request.POST.get("ustatus","")
        if(id != "" and ustatus != ""):
            if(ustatus == "0"):
                ustatus = 1
            else:
                ustatus = 0
            try:
                obj = Category.objects.get(id=sid)
                obj.Status = ustatus
                obj.save()
                return HttpResponse("done")
            except:
                return HttpResponse("Invalid Request")
    else:
        return HttpResponse("Invalid Request")

@never_cache
def addproduct(request):
    if request.method == "POST":
        txtname = request.POST.get("txtname","")
        txtdesc = request.POST.get("txtdesc","")
        txtprice = request.POST.get("txtprice","")
        txtqty = request.POST.get("txtqty","")
        txtkeywords = request.POST.get("txtkeywords","")
        selectbrand = request.POST.get("selectbrand","")
        selectcategory = request.POST.get("selectcategory","")
        imgproduct = request.FILES.get("imgproduct","")
        if(valid_image_size(imgproduct)):
            obj = Product.objects.filter(Name=txtname, ProductBrand=selectbrand, ProductCat=selectcategory)
            if(len(obj) > 0):
                messages.error(request, "This product is already added!")
            else:
                try:
                    category = Category.objects.get(id=selectcategory)
                    brand = Brand.objects.get(id=selectbrand)
                    product = Product(Name=txtname, Desc=txtdesc, Image=imgproduct, Price=txtprice, Quantity=txtqty, Keywords=txtkeywords, ProductBrand=brand, ProductCat=category)
                    product.save()
                    messages.success(request, "Product added successfully!")
                except:
                    messages.error(request, "Something went wrong!")
        else:
            messages.error(request, "The file must be an image and size less than 2 MB!")
    categories = Category.objects.filter(Status=1)
    brands = Brand.objects.filter(Status=1)
    params = {
        "categories": categories,
        "brands": brands
    }
    return render(request, "FarmersBuddy/Admin/addproduct.html", params)

@never_cache
def manageproducts(request):
    products = Product.objects.all()
    params = {
        "products": products
    }
    return render(request, "FarmersBuddy/Admin/manageproducts.html", params)

def changeproductstatus(request):
    if request.method == "POST":
        pid = request.POST.get("id", "")
        ustatus = request.POST.get("ustatus", "")
        if (pid != "" and ustatus != ""):
            if (ustatus == "0"):
                ustatus = 1
            else:
                ustatus = 0
            try:
                obj = Product.objects.get(id=pid)
                obj.Status = ustatus
                obj.save()
                return HttpResponse("done")
            except:
                return HttpResponse("Invalid Request")
    else:
        return HttpResponse("Invalid Request")

def deleteproduct(request):
    if request.method == "POST":
        pid = request.POST.get("id", "")
        if (pid != ""):
            try:
                obj = Product.objects.get(id=pid)
                obj.delete()
                return HttpResponse("done")
            except:
                return HttpResponse("Invalid Request")
    else:
        return HttpResponse("Invalid Request")

@never_cache
def editproduct(request):
    pid = request.GET.get("pid", "")
    data = Product.objects.get(id=pid)
    categories = Category.objects.filter(Status=1)
    brands = Brand.objects.filter(Status=1)
    params = {
        "data": data,
        "categories": categories,
        "brands": brands
    }
    if request.method == "POST":
        if request.POST.get("UpdateProductImage") != None:
            imgproduct = request.FILES.get("imgproduct", "")
            if (valid_image_size(imgproduct)):
                obj = Product.objects.get(id=pid)
                obj.Image = imgproduct
                obj.save()
                messages.success(request, "Product image updated successfully!")
                return redirect(manageproducts)
            else:
                messages.error(request, "The file must be an image and size less than 2 MB!")
        elif request.POST.get("UpdateProductDetails") != None:
            txtname = request.POST.get("txtname", "")
            txtdesc = request.POST.get("txtdesc", "")
            txtprice = request.POST.get("txtprice", "")
            txtqty = request.POST.get("txtqty", "")
            txtkeywords = request.POST.get("txtkeywords", "")
            selectbrand = request.POST.get("selectbrand", "")
            selectcategory = request.POST.get("selectcategory", "")

            obj = Product.objects.get(id=pid)
            category = Category.objects.get(id=selectcategory)
            brand = Brand.objects.get(id=selectbrand)
            obj.Name = txtname
            obj.Desc = txtdesc
            obj.Price = txtprice
            obj.Quantity = txtqty
            obj.Keywords = txtkeywords
            obj.ProductBrand = brand
            obj.ProductCat = category
            obj.save()
            messages.success(request, "Product updated successfully!")
            return redirect(manageproducts)
    return render(request, "FarmersBuddy/Admin/editproduct.html", params)

@never_cache
def products(request):
    if "id" not in request.session:
        return redirect(index)
    products = Product.objects.filter(Status=1)
    cats = set()
    for pro in products:
        x = pro.ProductCat.CategoryName
        cats.add(x)
    params = {
        "categories": cats,
        "products": products
    }
    if request.method == "POST":
        pid = request.POST.get("pid","")
        if(pid != ""):
            user = Userx.objects.get(id=request.session['id'])
            product = Product.objects.get(id=pid)

            count = Cart.objects.filter(UserId=user, ProductId=product)
            if len(count) > 0:
                messages.warning(request, "Product already present in the cart!")
            else:
                obj = Cart(ProductId = product, UserId = user)
                obj.save()
                messages.success(request, "Product added to the cart!")
        else:
            messages.error(request, "Something went wrong!")
    return render(request, "FarmersBuddy/Home/products.html", params)

@never_cache
def viewproduct(request):
    pid = request.GET.get("pid","")
    product = Product.objects.get(id=pid, Status=1)
    params = {
        "product": product
    }
    return render(request, "FarmersBuddy/Home/viewproduct.html", params)

@never_cache
def cart(request):
    if request.method == "POST":
        if request.POST.get("syncqty") != None:
            try:
                cid = request.POST.get("cid","")
                qty = request.POST.get("qty","")
                obj = Cart.objects.get(id=cid)
                obj.Quantity = qty
                obj.save()
                messages.success(request, "Quantity updated successfully!")
            except:
                print("hi")
                messages.error(request,"Something went wrong!")
        elif request.POST.get("deleteproduct") != None:
            try:
                cid = request.POST.get("cid", "")
                obj = Cart.objects.get(id=cid)
                obj.delete()
                messages.success(request, "Product removed successfully!")
            except:
                messages.error(request, "Something went wrong!")
    if "id" not in request.session:
        return redirect(index)
    userid = Userx.objects.get(id=request.session['id'])
    products = Cart.objects.filter(UserId=userid,Status=0)
    params = {
        "products" : products
    }
    return render(request, "FarmersBuddy/Home/cart.html",params)

@never_cache
def checkout(request):
    userid = Userx.objects.get(id=request.session['id'])
    products = Cart.objects.filter(UserId=userid, Status=0)
    total = 0
    for i in products:
        price = i.ProductId.Price * i.Quantity
        total += price
    params = {
        "products": products,
        "total": total
    }
    return render(request, "FarmersBuddy/Home/checkout.html",params)

@never_cache
def confirmorder(request):
    user = Userx.objects.get(id=request.session['id'])
    products = Cart.objects.filter(UserId=user, Status=0)
    total = 0
    for i in products:
        price = i.ProductId.Price * i.Quantity
        total += price
    params = {
        "products": products,
        "total": total,
        "user" : user
    }
    request.session["totalamount"] = total
    return render(request, "FarmersBuddy/Home/confirmorder.html",params)

@never_cache
def success(request):
    user = Userx.objects.get(id=request.session['id'])
    products = Cart.objects.filter(UserId=user,Status=0)
    total = request.session["totalamount"]
    latest = Order.objects.latest("OrderId")
    oid = latest.OrderId + 1
    Cart.objects.filter(UserId=user,Status=0).update(Status=1)
    for pro in products:
        obj = Order(OrderId=oid, ProductId=pro.ProductId, UserId=user, Quantity=pro.Quantity, TotalAmount=total)
        print(obj.save())
    return render(request, "FarmersBuddy/Home/success.html")

@never_cache
def about(request):
    return render(request, "FarmersBuddy/Home/about.html")

@never_cache
def contact(request):
    return render(request, "FarmersBuddy/Home/contact.html")

@never_cache
def manageorders(request):
    obj = Order.objects.all()
    orders = set()
    for i in obj:
        x = i.OrderId
        orders.add(x)
    print(orders)
    params = {
        "orders": orders,
        "data": obj
    }
    return render(request, "FarmersBuddy/Admin/manageorders.html", params)


def changepassword(request):
    if "id" not in request.session:
        return redirect(index)
    if request.method == "POST":
        txtpass = request.POST.get("txtpass","")
        txtpass1 = request.POST.get("txtpass1", "")
        txtpass2 = request.POST.get("txtpass2", "")
        if txtpass != "" and txtpass1 != "" and txtpass2 != "":
            if(txtpass1 == txtpass2):
                txtpass = hashlib.sha256(txtpass.encode())
                txtpass1 = hashlib.sha256(txtpass1.encode())

                obj = Userx.objects.filter(id=request.session["id"], Password = txtpass.hexdigest())
                if len(obj) == 1:
                    obj = Userx.objects.get (id=request.session["id"])
                    obj.Password = txtpass1.hexdigest()
                    obj.save()
                    messages.success(request, "Your password changed successfully!")
                else:
                    messages.error(request, "Your current password is Invalid!")
            else:
                messages.error(request, "New Password and Re-Entered Password are not same!")
        else:
            messages.error(request, "Empty form!")
    return render(request, "FarmersBuddy/Home/changepassword.html")

@never_cache
def editprofile(request):
    if "id" not in request.session:
        return redirect(index)
    if request.method == "POST":
        txtfname = request.POST.get("txtfname", "")
        txtlname = request.POST.get("txtlname", "")
        txtmobile = request.POST.get("txtmobile", "")
        txtaddress = request.POST.get("txtaddress", "")
        if txtfname!= "" and txtlname != "" and txtmobile != "" and txtaddress != "":
            obj = Userx.objects.get(id=request.session["id"])
            obj.FirstName = txtfname
            obj.LastName = txtlname
            obj.Mobile = txtmobile
            obj.Address1 = txtaddress
            obj.save()
            messages.success(request, "Your details updated successfully!")
        else:
            messages.error(request, "Empty Form!s")
    user = Userx.objects.get(id=request.session["id"])
    params = {
        "user":user,
    }
    return render(request, "FarmersBuddy/Home/editprofile.html", params)


def forgotpassword(request):
    if request.method == "POST":
        txtemail = request.POST.get("txtemail","")
        if(txtemail != ""):
            count = Userx.objects.filter(Email=txtemail)
            if len(count) == 1:
                otp = random.randint(111111, 999999)
                request.session['otp'] = otp
                request.session["email"] = txtemail
                sendemail(txtemail,"OTP for Forgot Password", "Your OTP for forgot password is: " + str(otp))
                return redirect(verifyotp)
            else:
                messages.error(request, "Please enter registered email only!")
        else:
            messages.error(request, "Empty form!")
    return render(request, "FarmersBuddy/Home/forgotpassword.html")


def verifyotp(request):
    otp = request.session['otp']
    email = str(request.session['email'])
    if request.method == "POST":
        txtotp = request.POST.get("txtotp", "")
        if (txtotp != ""):
            if (txtotp == str(otp)):
                obj = Userx.objects.get(Email=email)
                obj.Status = "1"
                obj.save()
                request.session['id'] = obj.id
                return redirect(newpassword)
            else:
                messages.error(request, "Invalid OTP")
        else:
            messages.error(request, "Empty from!")
    return render(request, "FarmersBuddy/Home/verifyotp.html")


def newpassword(request):
    if "id" not in request.session:
        return redirect(index)
    if request.method == "POST":
        txtpass1 = request.POST.get("txtpass1", "")
        txtpass2 = request.POST.get("txtpass2", "")
        if txtpass1 != "" and txtpass2 != "":
            if(txtpass1 == txtpass2):
                txtpass1 = hashlib.sha256(txtpass1.encode())
                obj = Userx.objects.get (id=request.session["id"])
                obj.Password = txtpass1.hexdigest()
                obj.save()
                del request.session['id']
                del request.session['email']
                del request.session['otp']
                messages.success(request, "Your password changed successfully!")
                return redirect(login)
            else:
                messages.error(request, "New Password and Re-Entered Password are not same!")
        else:
            messages.error(request, "Empty form!")
    return render(request, "FarmersBuddy/Home/newpassword.html")