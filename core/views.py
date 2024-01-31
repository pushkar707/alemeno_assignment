import json
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from core.models import Customer

from core.utils import round_to_nearest_lakh

def home(request):
    return HttpResponse("API healthy!!")

def register(request):
    if(request.method=="POST"):
        body = json.loads(request.body.decode('utf-8'))
        print(list(body))
        if(['first_name',"last_name","age","monthly_income","phone_number"] == list(body)):
            body['approved_limit'] = round_to_nearest_lakh(36*body['monthly_income'])
            body['monthly_salary'] = body['monthly_income']
            body.pop('monthly_income')
            try:
                Customer.objects.create(**body)
            except Exception as e:
                print("error occured while creating customer")
                print(e)
        else:
            return JsonResponse({"error":"Missing required body arguments"})
        return JsonResponse(body)