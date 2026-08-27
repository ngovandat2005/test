from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('gioi-thieu/', views.about, name='about'),
    path('san-pham/', views.product_list, name='product_list'),
    path('san-pham/<slug:slug>/', views.product_detail, name='product_detail'),
    path('tin-tuc/', views.news_list, name='news_list'),
    path('tin-tuc/<slug:slug>/', views.news_detail, name='news_detail'),
    path('dai-ly-phan-phoi/', views.distributors, name='distributors'),
    path('dang-ky-dai-ly/', views.dealer_register, name='dealer_register'),
    path('lien-he/', views.contact, name='contact'),
    path('e-catalogue/', views.catalogue, name='catalogue'),
    path('cong-cu-tinh/', views.calculator, name='calculator'),
    path('du-an/', views.project_list, name='project_list'),
    path('du-an/<slug:slug>/', views.project_detail, name='project_detail'),
    path('dang-ky-tu-van/', views.consultation, name='consultation'),
]
