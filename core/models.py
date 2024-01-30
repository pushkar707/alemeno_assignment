from django.db import models
from django.utils import timezone

class Customer(models.Model):
    customerId =  models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=12,null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    monthly_salary = models.IntegerField(null=True, blank=True)
    approved_limit = models.IntegerField(null=True, blank=True)
    current_debt = models.IntegerField(null=True, blank=True)
    
class Loan:
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,null=True)
    loan_id = models.AutoField(primary_key=True)
    loan_amount = models.IntegerField(null=False,blank=False)
    tenure = models.FloatField(null=False, blank=False)
    interest_rate = models.FloatField(null=False, blank=False)
    monthly_repayment = models.IntegerField(null=False,blank=False)
    emis_paid_on_time = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

