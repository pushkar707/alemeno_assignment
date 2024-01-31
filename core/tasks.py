from celery import shared_task
import pandas as pd
from core.models import Customer,Loan

@shared_task
def upload_initial_data(customer_file_path, loan_file_path):
    check = Customer.objects.exists()
    if(not check):
        df = pd.read_excel(customer_file_path)
        for index, row in df.iterrows():
            Customer.objects.create(**row)

        df = pd.read_excel(loan_file_path)
        for index, row in df.iterrows():
            Loan.objects.create(**row)
