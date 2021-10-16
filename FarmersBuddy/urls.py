from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registration/', views.registration, name='registration'),
    path('login/', views.login, name='login'),
    path('verify/', views.verify, name='verify'),
    path('logout/', views.logout, name='logout'),

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

]