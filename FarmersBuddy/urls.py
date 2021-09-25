from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registration/', views.registration, name='registration'),
    path('login/', views.login, name='login'),
    path('verify/', views.verify, name='verify'),
    path('logout/', views.logout, name='logout'),
    path('admin/dashboard', views.admindashboard, name='admindashboard'),
    
    # Customers crud
    path('admin/customers', views.customers, name='customers'),
    path('admin/customers/changestatus', views.changestatus, name='changestatus'),
    path('admin/customers/deletecustomer', views.deletecustomer, name='deletecustomer'),
    
    # Brands crud
    path('admin/managebrands', views.managebrands, name='managebrands'),
    path('admin/changebrandstatus', views.changebrandstatus, name='changebrandstatus'),
    path('admin/deletebrand', views.deletebrand, name='deletebrand'),

    # Categories
    path('admin/managecategories', views.managecategories, name='managecategories'),

]