import os
from django.apps import AppConfig, apps
from django.db import connection

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        with connection.cursor() as cursor:
            from celery import shared_task
            import pandas as pd
            from core.models import Customer,Loan

            @shared_task
            def upload_initial_data(customer_file_path, loan_file_path):    
                df = pd.read_excel(customer_file_path)
                for index, row in df.iterrows():
                    Customer.objects.create(**row)

                df = pd.read_excel(loan_file_path)
                for index, row in df.iterrows():
                    Loan.objects.create(**row)


            customer_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'customer_data.xlsx')
            loan_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'loan_data.xlsx')
            check = Customer.objects.exists()
            if(not check):
                upload_initial_data.delay(customer_file_path,loan_file_path)
        print("Your custom startup code has been executed.")
