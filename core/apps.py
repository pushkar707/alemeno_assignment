import os
import sys
from django.apps import AppConfig, apps
from django.db import connection

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        if 'runserver' not in sys.argv:
            print(sys.argv)
            return
        with connection.cursor() as cursor:
            from core.models import Customer
            from core.tasks import upload_initial_data

            customer_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'customer_data.xlsx')
            loan_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'loan_data.xlsx')
            check = Customer.objects.exists()
            if(not check):
                upload_initial_data.delay(customer_file_path,loan_file_path)
        print("Your custom startup code has been executed.")
