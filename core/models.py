from django.db import models
from django.db.models import Max


class Customer(models.Model):
    customer_id =  models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=12,null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    monthly_salary = models.IntegerField(null=True, blank=True)
    approved_limit = models.IntegerField(null=True, blank=True)
    current_debt = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.customer_id is None:
            # Generate a new unique customer_id only if it's not provided manually
            self.customer_id = self.generate_unique_customer_id()

        # Ensure uniqueness when saving the object
        if Customer.objects.filter(customer_id=self.customer_id).exclude(pk=self.pk).exists():
            # If the generated customer_id conflicts with existing records, generate a new unique value
            self.customer_id = self.generate_unique_customer_id()

        super().save(*args, **kwargs)

    def generate_unique_customer_id(self):
        # Implement your logic to generate a unique customer_id
        # For example, you might query the database for the highest existing customer_id and add 1
        max_customer_id = Customer.objects.all().aggregate(Max('customer_id'))['customer_id__max']  # noqa: F821
        return max_customer_id + 1 if max_customer_id is not None else 1

    
class Loan(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,null=True)
    loan_id = models.IntegerField(null=False, blank=False)
    loan_amount = models.IntegerField(null=False,blank=False)
    tenure = models.FloatField(null=False, blank=False)
    interest_rate = models.FloatField(null=False, blank=False)
    monthly_repayment = models.IntegerField(null=False,blank=False)
    emis_paid_on_time = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

