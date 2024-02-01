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
                def process_excel_file(file_path, model_class):
                    df = pd.read_excel(file_path)
                    model_objects = [model_class(**row) for index, row in df.iterrows()]
                    model_class.objects.bulk_create(model_objects)
  
                process_excel_file(customer_file_path, Customer)
                process_excel_file(loan_file_path, Loan)

            customer_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'customer_data.xlsx')
            loan_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'loan_data.xlsx')
            check = Customer.objects.exists()
            if(not check):
                upload_initial_data.delay(customer_file_path,loan_file_path)
        print("Your custom startup code has been executed.")
