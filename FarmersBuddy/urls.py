from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('registration/', views.registration, name='registration'),
    path('login/', views.login, name='login'),
    path('verify/', views.verify, name='verify'),
    path('logout/', views.logout, name='logout'),
    path('changepassword/', views.changepassword, name='changepassword'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('verifyotp/', views.verifyotp, name='verifyotp'),
    path('newpassword/', views.newpassword, name='newpassword'),

    # Admin dashboard
    path('admin/dashboard', views.admindashboard, name='admindashboard'),
    
    # Customers crud
    path('admin/customers', views.customers, name='customers'),
    path('admin/customers/changestatus', views.changestatus, name='changestatus'),
    path('admin/customers/deletecustomer', views.deletecustomer, name='deletecustomer'),
    
    # Brands crud
    path('admin/managebrands', views.managebrands, name='managebrands'),
    path('admin/changebrandstatus', views.changebrandstatus, name='changebrandstatus'),
    path('admin/updatebrand', views.updatebrand, name='updatebrand'),
    path('admin/deletebrand', views.deletebrand, name='deletebrand'),

    # Categories crud
    path('admin/managecategories', views.managecategories, name='managecategories'),
    path('admin/changecategorystatus', views.changecategorystatus, name='changecategorystatus'),
    path('admin/updatecategory', views.updatecategory, name='updatecategory'),
    path('admin/deletecategory', views.deletecategory, name='deletecategory'),

    # Products crud
    path('admin/addproduct', views.addproduct, name='addproduct'),
    path('admin/editproduct', views.editproduct, name='editproduct'),
    path('admin/deleteproduct', views.deleteproduct, name='deleteproduct'),
    path('admin/manageproducts', views.manageproducts, name='manageproducts'),
    path('admin/changeproductstatus', views.changeproductstatus, name='changeproductstatus'),

    # User view products
    path('products', views.products, name='products'),
    path('viewproduct', views.viewproduct, name='viewproduct'),

    # cart
    path('cart', views.cart, name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('confirmorder', views.confirmorder, name='confirmorder'),
    path('success', views.success, name='success'),

    # orders
    path('manageorders', views.manageorders, name='manageorders'),
    path('vieworders', views.vieworders, name='vieworders'),
    path('orderdetails', views.orderdetails, name='orderdetails'),
    path('vieworderdetails', views.vieworderdetails, name='vieworderdetails'),
    path('changeorderstatus', views.changeorderstatus, name='changeorderstatus'),

    # Reports
    path('customerreport', views.customerreport, name='customerreport'),
    path('productsreport', views.productsreport, name='productsreport'),
    path('salesreport', views.salesreport, name='salesreport'),

    # Bill
    path('invoice', views.invoice, name='invoice'),

    # Blogs
    path('manageblogs', views.manageblogs, name='manageblogs'),
    path('changeblogstatus', views.changeblogstatus, name='changeblogstatus'),
    path('deleteblog', views.deleteblog, name='deleteblog'),
    path('addblog', views.addblog, name='addblog'),
    path('editblog', views.editblog, name='editblog'),
    path('viewblogs', views.viewblogs, name='viewblogs'),
    path('displayblog', views.displayblog, name='displayblog'),

    # Feedback
    path('feedback', views.feedback, name='feedback'),
    path('admin/managefeedbacks', views.managefeedbacks, name='managefeedbacks'),
    path('admin/deletefeedback', views.deletefeedback, name='deletefeedback'),
]