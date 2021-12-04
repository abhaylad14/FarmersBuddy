import json
from math import ceil
from typing import Type
from django.shortcuts import render, redirect
import re, razorpay
from .models import *
import hashlib, random, smtplib
from django.contrib import messages
from django.http import HttpResponse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.views.decorators.cache import never_cache

MAX_SIZE = 2 * 1024 * 1024


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
        server.sendmail(sender, receiver, message.as_string())
        print("Successfully sent email")
        server.quit()
    except smtplib.SMTPException:
        print("Error: unable to send email")


@never_cache
def index(request):
    return render(request, "FarmersBuddy/Home/index.html")


@never_cache
def verify(request):
    otp = request.session['otp']
    email = str(request.session['email'])
    sendemail(email, "Verify Account", "Your verification OTP is: " + str(otp))
    if request.method == "POST":
        txtotp = request.POST.get("txtotp", "")
        if (txtotp != ""):
            if (txtotp == str(otp)):
                obj = Userx.objects.get(Email=email)
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
    return HttpResponse("<script>localStorage.clear();window.location.replace('http://127.0.0.1:8000/FarmersBuddy/');</script>")
    # return redirect(index)


@never_cache
def login(request):
    if request.method == "POST":
        txtemail = request.POST.get("txtemail", "")
        txtpass = request.POST.get("txtpass", "")
        print(txtemail, txtpass)
        if (txtemail != "" and txtpass != ""):
            pass1 = hashlib.sha256(txtpass.encode())
            check = Userx.objects.filter(Email=txtemail, Password=pass1.hexdigest(), Status="1")
            if (len(check) == 1):
                obj = Userx.objects.get(Email=txtemail)
                request.session['id'] = obj.id
                if obj.Type == "c":
                    return redirect(index)
                elif obj.Type == "a":
                    request.session['admin'] = True
                    return redirect(admindashboard)
            else:
                check = Userx.objects.filter(Email=txtemail, Password=pass1.hexdigest(), Status="2")
                if (len(check) == 1):
                    otp = random.randint(111111, 999999)
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
        txtlname = request.POST.get("txtlname", "")
        txtmobile = request.POST.get("txtmobile", "")
        txtaddress = request.POST.get("txtaddress", "")
        txtemail = request.POST.get("txtemail", "")
        txtpass1 = request.POST.get("txtpass1", "")
        txtpass2 = request.POST.get("txtpass2", "")

        if (txtfname != "" and txtlname != "" and txtmobile != "" and txtaddress != "" and txtemail != "" and
                txtpass1 != "" and txtpass2 != ""):
            if (re.search("^[a-zA-Z]{2,20}$", txtfname)):
                flagfname = 1
            else:
                errstr += "Please enter valid Firstname\t"

            if (re.search("^[a-zA-Z]{2,20}$", txtlname)):
                flaglname = 1
            else:
                errstr += "Please enter valid Lastname\t"

            if (re.search("^[0-9]{10}$", txtmobile)):
                flagmobile = 1
            else:
                errstr += "Mobile number is not valid\t"

            if (re.search("^[a-zA-Z,-/ ,0-9]+$", txtaddress)):
                flagaddress = 1
            else:
                errstr += "Address is invalid"

            if (re.search("[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", txtemail)):
                flagemail = 1
            else:
                errstr += "Please enter valid email\t"

            if (re.search("(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}", txtpass1)):
                flagpass1 = 1
            else:
                errstr += "Please enter a valid password\t"

            if (
                    flagfname == 1 and flaglname == 1 and flagmobile == 1 and flagaddress == 1 and flagemail == 1 and flagpass1 == 1):
                if (txtpass1 == txtpass2):
                    exists = Userx.objects.filter(Email=txtemail)
                    if (len(exists) > 0):
                        messages.warning(request, "The User already exists!")
                    else:
                        pass1 = hashlib.sha256(txtpass1.encode())
                        newUser = Userx(FirstName=txtfname, LastName=txtlname, Email=txtemail,
                                        Password=pass1.hexdigest(), Mobile=txtmobile, Address1=txtaddress)
                        newUser.save()
                        messages.success(request, "The User registered successfully!")
                else:
                    errstr += "Password and Re-Enter password does not match\t"
                    messages.error(request, errstr)
            else:
                messages.error(request, errstr)
        else:
            messages.error(request, "Invalid Request, Something went wrong!")
    return render(request, "FarmersBuddy/Home/registration.html")


# Admin Side
@never_cache
def admindashboard(request):
    obj = Userx.objects.filter(Type="c")
    customers = len(obj)
    obj = Order.objects.raw("select * from FarmersBuddy_Order where Status != '0' ")
    orders = len(obj)
    obj = Product.objects.filter(Status=1)
    products = len(obj)
    params = {
        "customers": customers,
        "orders": orders,
        "products": products
    }
    return render(request, "FarmersBuddy/Admin/dashboard.html", params)


@never_cache
def customers(request):
    users = Userx.objects.filter(Type="c")
    print(users)
    dictusers = {
        "user": users
    }
    return render(request, "FarmersBuddy/Admin/customers.html", dictusers)


def changestatus(request):
    if request.method == "POST":
        sid = request.POST.get("id", "")
        ustatus = request.POST.get("ustatus", "")
        if (id != "" and ustatus != ""):
            if (ustatus == "0"):
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
        cid = request.POST.get("id", "")
        print(cid)
        if (cid != ""):
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
        txtbrand = request.POST.get("txtbrand", "")
        txtbrand = txtbrand.strip()
        if (txtbrand != ""):
            obj = Brand.objects.filter(BrandName=txtbrand)
            if (len(obj) > 0):
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
        sid = request.POST.get("id", "")
        ustatus = request.POST.get("ustatus", "")
        if (id != "" and ustatus != ""):
            if (ustatus == "0"):
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
        bid = request.POST.get("id", "")
        ubrand = request.POST.get("ubrand", "")
        print(bid)
        if (bid != "" and ubrand != ""):
            try:
                obj = Brand.objects.filter(BrandName=ubrand)
                if (len(obj) > 0):
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
        cid = request.POST.get("id", "")
        print(cid)
        if (cid != ""):
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
        txtcategory = request.POST.get("txtcategory", "")
        txtcategory = txtcategory.strip()
        if (txtcategory != ""):
            obj = Category.objects.filter(CategoryName=txtcategory)
            if (len(obj) > 0):
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
        cid = request.POST.get("id", "")
        ucategory = request.POST.get("ucategory", "")
        print(cid)
        if (cid != "" and ucategory != ""):
            try:
                obj = Category.objects.filter(CategoryName=ucategory)
                if (len(obj) > 0):
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
        cid = request.POST.get("id", "")
        print(cid)
        if (cid != ""):
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
        sid = request.POST.get("id", "")
        ustatus = request.POST.get("ustatus", "")
        if (id != "" and ustatus != ""):
            if (ustatus == "0"):
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
        txtname = request.POST.get("txtname", "")
        txtdesc = request.POST.get("txtdesc", "")
        txtprice = request.POST.get("txtprice", "")
        txtqty = request.POST.get("txtqty", "")
        txtkeywords = request.POST.get("txtkeywords", "")
        selectbrand = request.POST.get("selectbrand", "")
        selectcategory = request.POST.get("selectcategory", "")
        imgproduct = request.FILES.get("imgproduct", "")
        if (valid_image_size(imgproduct)):
            obj = Product.objects.filter(Name=txtname, ProductBrand=selectbrand, ProductCat=selectcategory)
            if (len(obj) > 0):
                messages.error(request, "This product is already added!")
            else:
                try:
                    category = Category.objects.get(id=selectcategory)
                    brand = Brand.objects.get(id=selectbrand)
                    product = Product(Name=txtname, Desc=txtdesc, Image=imgproduct, Price=txtprice, Quantity=txtqty,
                                      Keywords=txtkeywords, ProductBrand=brand, ProductCat=category)
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
    product = Product.objects.filter(Status=1)
    cats = set()
    for pro in product:
        x = pro.ProductCat.CategoryName
        cats.add(x)
    params = {
        "categories": cats,
        "products": product
    }
    if request.method == "POST":
        txtsearch = request.POST.get("txtsearch", "")
        if txtsearch != "":
            items = Product.objects.filter(Keywords__contains=txtsearch)
            if len(items) > 0:
                cats = set()
                for item in items:
                    x = item.ProductCat.CategoryName
                    cats.add(x)
                params = {
                    "categories": cats,
                    "products": items
                }
                return render(request, "FarmersBuddy/Home/products.html", params)
            else:
                messages.info(request, "No product found!")
                # return redirect(products)
        else:
            txtcart = request.POST.get("txtcart", "")
            request.session["cart"] = txtcart
            return HttpResponse("done")
    return render(request, "FarmersBuddy/Home/products.html", params)


@never_cache
def viewproduct(request):
    pid = request.GET.get("pid", "")
    product = Product.objects.get(id=pid, Status=1)
    params = {
        "product": product
    }
    return render(request, "FarmersBuddy/Home/viewproduct.html", params)


@never_cache
def cart(request):
    if "cart" in request.session:
        try:
            cart = request.session["cart"]
            cart = json.loads(cart)
            cartpid = []
            for key in cart.keys():
                cartpid.append(int(key))
            product = []
            for i in cartpid:
                x = Product.objects.get(id=i)
                product.append(x)
            print(products)
            params = {
                "products": product
            }
            return render(request, "FarmersBuddy/Home/cart.html", params)
        except:
            return redirect(products)
    return render(request, "FarmersBuddy/Home/cart.html")


@never_cache
def checkout(request):
    if "id" not in request.session:
        return redirect(login)
    if "cart" not in request.session:
        return redirect(products)
    cart = request.session["cart"]
    cart = json.loads(cart)
    pro = []
    for key in cart.keys():
        obj = Product.objects.get(id=key)
        pro.append(obj)
    userid = Userx.objects.get(id=request.session['id'])
    total = 0
    for i in pro:
        x = i.id
        price = i.Price * cart[str(x)]
        total += price
    request.session["total"] = total
    params = {
        "products": pro,
        "total": total
    }
    return render(request, "FarmersBuddy/Home/checkout.html", params)


@never_cache
def confirmorder(request):
    # check sessions
    if "id" not in request.session:
        return redirect(login)
    if "cart" not in request.session:
        return redirect(products)
    if "total" not in request.session:
        return redirect(products)

    # change address request
    txtaddress = ""
    if request.method == "POST":
        txtaddress = request.POST.get("txtaddress", "")
        if txtaddress != "":
            pass
        else:
            messages.error(request, "Empty Address field!")
    # get objects and values
    user = Userx.objects.get(id=request.session['id'])
    total = request.session["total"]
    cart = request.session["cart"]
    cart = json.loads(cart)
    request.session["address"] = txtaddress
    obj = Order.objects.filter(Status=0, User=user)
    # check if order cart already exists
    if (len(obj) == 0):
        order = Order(User=user, Data=request.session["cart"], Total=total, Address=txtaddress)
        order.save()
    else:
        order = Order.objects.get(User=user, Status=0)
        order.Address = txtaddress
        order.Data = request.session["cart"]
        order.save()

    # retrieve products
    pro = []
    for key in cart.keys():
        obj = Product.objects.get(id=key)
        pro.append(obj)

    # check avalability
    available = True
    for item in pro:
        qty = item.Quantity
        x = cart[str(item.id)]
        if (qty - x > 0):
            pass
        else:
            available = False
            messages.error(request, "Not enough stock available!")
            break
    if (available):
        params = {
            "products": pro,
            "total": total,
            "user": user
        }
        return render(request, "FarmersBuddy/Home/confirmorder.html", params)
    return redirect(products)


@never_cache
def success(request):
    if "id" in request.session:
        user = Userx.objects.get(id=request.session['id'])
        cart = request.session["cart"]
        cart = json.loads(cart)
        for key, value in cart.items():
            pro = Product.objects.get(id=int(key))
            cartqty = value
            totalqty = pro.Quantity
            totalqty = totalqty - cartqty
            pro.Quantity = totalqty
            pro.save()
        obj = Order.objects.get(User=user, Status=0)
        # set default address
        if (obj.Address == ""):
            obj.Address = user.Address1
        obj.Status = 1
        obj.save()
        if "cart" in request.session:
            del request.session["cart"]
        if "address" in request.session:
            del request.session["address"]
        return render(request, "FarmersBuddy/Home/success.html")
    else:
        return redirect(products)


@never_cache
def about(request):
    return render(request, "FarmersBuddy/Home/about.html")


@never_cache
def contact(request):
    return render(request, "FarmersBuddy/Home/contact.html")


@never_cache
def manageorders(request):
    orders = Order.objects.raw("select * from FarmersBuddy_Order where Status='1' or Status='2' ")
    params = {
        "orders": orders,
    }
    return render(request, "FarmersBuddy/Admin/manageorders.html", params)


def changepassword(request):
    if "id" not in request.session:
        return redirect(index)
    if request.method == "POST":
        txtpass = request.POST.get("txtpass", "")
        txtpass1 = request.POST.get("txtpass1", "")
        txtpass2 = request.POST.get("txtpass2", "")
        if txtpass != "" and txtpass1 != "" and txtpass2 != "":
            if (txtpass1 == txtpass2):
                txtpass = hashlib.sha256(txtpass.encode())
                txtpass1 = hashlib.sha256(txtpass1.encode())

                obj = Userx.objects.filter(id=request.session["id"], Password=txtpass.hexdigest())
                if len(obj) == 1:
                    obj = Userx.objects.get(id=request.session["id"])
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
        if txtfname != "" and txtlname != "" and txtmobile != "" and txtaddress != "":
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
        "user": user,
    }
    return render(request, "FarmersBuddy/Home/editprofile.html", params)


@never_cache
def forgotpassword(request):
    if request.method == "POST":
        txtemail = request.POST.get("txtemail", "")
        if (txtemail != ""):
            count = Userx.objects.filter(Email=txtemail)
            if len(count) == 1:
                otp = random.randint(111111, 999999)
                request.session['otp'] = otp
                request.session["email"] = txtemail
                sendemail(txtemail, "OTP for Forgot Password", "Your OTP for forgot password is: " + str(otp))
                return redirect(verifyotp)
            else:
                messages.error(request, "Please enter registered email only!")
        else:
            messages.error(request, "Empty form!")
    return render(request, "FarmersBuddy/Home/forgotpassword.html")


@never_cache
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


@never_cache
def newpassword(request):
    if "id" not in request.session:
        return redirect(index)
    if request.method == "POST":
        txtpass1 = request.POST.get("txtpass1", "")
        txtpass2 = request.POST.get("txtpass2", "")
        if txtpass1 != "" and txtpass2 != "":
            if (txtpass1 == txtpass2):
                txtpass1 = hashlib.sha256(txtpass1.encode())
                obj = Userx.objects.get(id=request.session["id"])
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


@never_cache
def vieworders(request):
    if "id" not in request.session:
        return redirect(index)
    user = Userx.objects.get(id=request.session["id"])
    orders = Order.objects.filter((models.Q(Status=1) | models.Q(Status=2)) & models.Q(User=user))
    print(orders)
    params = {
        "orders": orders
    }
    return render(request, "FarmersBuddy/Home/vieworders.html", params)


@never_cache
def orderdetails(request):
    if "id" not in request.session:
        return redirect(index)
    oid = request.GET.get("oid", "")
    if oid != "":
        order = Order.objects.get(id=oid)
        data = json.loads(order.Data)
        products = []
        for key, value in data.items():
            x = Product.objects.get(id=key)
            x.qty = value
            products.append(x)
        params = {
            "products": products,
            "order": order
        }
        return render(request, "FarmersBuddy/Home/orderdetails.html", params)
    return redirect(index)


@never_cache
def vieworderdetails(request):
    oid = request.GET.get("oid", "")
    if oid != "":
        order = Order.objects.get(id=oid)
        data = json.loads(order.Data)
        products = []
        for key, value in data.items():
            x = Product.objects.get(id=key)
            x.qty = value
            products.append(x)
        params = {
            "products": products,
            "order": order
        }
    return render(request, "FarmersBuddy/Admin/vieworderdetails.html", params)


def changeorderstatus(request):
    if request.method == "POST":
        oid = request.POST.get("oid", "")
        if (oid != ""):
            try:
                obj = Order.objects.get(id=oid)
                obj.Status = 2
                obj.save()
                return HttpResponse("done")
            except:
                return HttpResponse("Invalid Request")
    else:
        return HttpResponse("Invalid Request")


@never_cache
def customerreport(request):
    customers = Userx.objects.filter(Type="c")
    params = {
        "customers": customers
    }
    return render(request, "FarmersBuddy/Admin/customerreport.html", params)


@never_cache
def productsreport(request):
    products = Product.objects.all()
    params = {
        "products": products
    }
    return render(request, "FarmersBuddy/Admin/productsreport.html", params)


@never_cache
def salesreport(request):
    orders = Order.objects.filter(models.Q(Status=1) | models.Q(Status=2))
    products = []
    for item in orders:
        x = json.loads(item.Data)
        for key, value in x.items():
            p = Product.objects.get(id=int(key))
            p.qty = value
            p.sts = item.Status
            products.append(p)
    params = {
        "products": products
    }
    return render(request, "FarmersBuddy/Admin/salesreport.html", params)


@never_cache
def invoice(request):
    if "id" not in request.session:
        return redirect(index)
    iid = request.GET.get("iid", "")
    if iid != "":
        orders = Order.objects.get(id=iid)
        products = []
        x = json.loads(orders.Data)
        for key, value in x.items():
            p = Product.objects.get(id=int(key))
            p.qty = value
            products.append(p)
        params = {
            "orders": orders,
            "products": products
        }
        return render(request, "FarmersBuddy/Home/invoice.html", params)
    else:
        return redirect(index)


def manageblogs(request):
    blogs = Blog.objects.all()
    params = {
        "blogs": blogs
    }
    return render(request, "FarmersBuddy/Admin/manageblogs.html", params)


def changeblogstatus(request):
    if request.method == "POST":
        bid = request.POST.get("bid", "")
        ustatus = request.POST.get("ustatus", "")
        if (bid != "" and ustatus != ""):
            if (ustatus == "0"):
                ustatus = 1
            else:
                ustatus = 0
            try:
                obj = Blog.objects.get(id=bid)
                obj.Status = ustatus
                obj.save()
                return HttpResponse("done")
            except:
                return HttpResponse("Invalid Request")
    return HttpResponse("Invalid Request1")


def deleteblog(request):
    if request.method == "POST":
        bid = request.POST.get("bid","")
        if(bid != ""):
            try:
                obj = Blog.objects.get(id=bid)
                obj.delete()
                return HttpResponse("done")
            except:
                return HttpResponse("Invalid Request")
    else:
        return HttpResponse("Invalid Request")

@never_cache
def addblog(request):
    if request.method == "POST":
        txttitle = request.POST.get("txttitle","")
        txtdesc = request.POST.get("txtdesc", "")
        if(txttitle != "" and txtdesc != ""):
            try:
                obj = Blog(Title=txttitle, Desc= txtdesc)
                obj.save()
                messages.success(request, "Blog added successfully!")
            except:
                messages.error(request, "Something went wrong!")
        else:
            messages.error(request, "Empty form!")
    return render(request, "FarmersBuddy/Admin/addblog.html")

@never_cache
def editblog(request):
    bid = request.GET.get("bid","")
    if request.method == "POST":
        txttitle = request.POST.get("txttitle","")
        txtdesc = request.POST.get("txtdesc", "")
        if(bid != "" and txttitle != "" and txtdesc != ""):
            try:
                blog = Blog.objects.get(id=bid)
                blog.Title = txttitle
                blog.Desc = txtdesc
                blog.save()
                messages.success(request, "Blog updated successfully!")
                return redirect(manageblogs)
            except:
                messages.error(request, "Something went wrong!")
        else:
            messages.error(request, "Empty form!")
    if(bid != ""):
        try:
            blog = Blog.objects.get(id=bid)
            params = {
                "blog" : blog
            }
        except:
            return redirect(manageblogs)
        return render(request, "FarmersBuddy/Admin/editblog.html", params)
    else:
        return redirect(manageblogs)

@never_cache
def viewblogs(request):
    blogs = Blog.objects.filter(Status=1)
    params = {
        "blogs": blogs
    }
    return render(request, "FarmersBuddy/Home/blogs.html", params)

@never_cache
def displayblog(request):
    bid = request.GET.get("bid","")
    if bid != "":
        try:
            blog = Blog.objects.get(id=bid)
            params = {
                "blog": blog
            }
            return render(request, "FarmersBuddy/Home/viewblog.html", params)
        except:
            return redirect(viewblogs)
    else:
        redirect(viewblogs)

@never_cache
def searchproducts(request):
    if request.method == "POST":
        txtsearch = request.POST.get("txtsearch","")
        if txtsearch != "":
            items = Product.objects.filter(Keywords__contains=txtsearch)
            if len(items) > 0:
                cats = set()
                for item in items:
                    x = item.ProductCat.CategoryName
                    cats.add(x)
                params = {
                    "categories": cats,
                    "products" : items
                }
                return render(request, "FarmersBuddy/Home/searchproducts.html", params)
            else:
                messages.info(request, "No product found!")
                # return redirect(products)
        else:
            messages.error(request,"Invalid Request!")

@never_cache
def feedback(request):
    if "id" not in request.session:
        return redirect(login)
    if request.method == "POST":
        txttitle = request.POST.get("txttitle", "")
        txtdesc = request.POST.get("txtdesc","")
        if txttitle != "" and txtdesc != "":
            user = Userx.objects.get(id=request.session["id"])
            obj = Feedback.objects.filter(Title = txttitle, Desc= txtdesc, User=user)
            if len(obj) == 0:
                try:
                    feedback = Feedback(Title = txttitle, Desc = txtdesc, User=user)
                    feedback.save()
                    messages.success(request, "Feedback submitted successfully!")
                except:
                    messages.error(request, "Something went wrong!")
            else:
                messages.error(request, "Feedback already submitted!")
        else:
            messages.error(request, "Empty Form!")
    return render(request, "FarmersBuddy/Home/feedback.html")

@never_cache
def managefeedbacks(request):
    feedbacks = Feedback.objects.all()
    params = {
        "feedbacks": feedbacks
    }
    return render(request, "FarmersBuddy/Admin/managefeedbacks.html", params)


def deletefeedback(request):
    if request.method == "POST":
        fid = request.POST.get("fid", "")
        if (fid != ""):
            try:
                obj = Feedback.objects.get(id=fid)
                obj.delete()
                return HttpResponse("done")
            except:
                return HttpResponse("Invalid Request")
    else:
        return HttpResponse("Invalid Request")