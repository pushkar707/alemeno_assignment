import os
from django.shortcuts import render, HttpResponse
from core.tasks import upload_initial_data

def ingest_data_view(request):
    customer_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'customer_data.xlsx')
    loan_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'loan_data.xlsx')
    upload_initial_data.delay(customer_file_path,loan_file_path)
    return HttpResponse("Data ingestion task queued.")
