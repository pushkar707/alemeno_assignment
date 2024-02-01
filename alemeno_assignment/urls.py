"""
URL configuration for alemeno_assignment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core.views import home,register,create_loan,view_loan,view_customer_loan,check_eligibility

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home,name='home'),
    path('register', register,name='register'),
    path('check-eligibility', check_eligibility,name='check_eligibility'),
    path('create-loan', create_loan,name='create_loan'),
    path('view-loan/<loan_id>', view_loan,name='view_loan'),
    path('view-loans/<customer_id>', view_customer_loan,name='view_customer_loan'),
]
