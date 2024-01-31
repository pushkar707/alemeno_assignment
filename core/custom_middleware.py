import os
from core.tasks import upload_initial_data

class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        customer_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'customer_data.xlsx')
        loan_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'loan_data.xlsx')
        upload_initial_data.delay(customer_file_path,loan_file_path)
        response = self.get_response(request)
        return response