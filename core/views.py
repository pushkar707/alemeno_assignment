import json
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from core.models import Customer, Loan
from datetime import date

from core.utils import calculate_monthly_installment, round_to_nearest_lakh

def home(request):
    return HttpResponse("API healthy!!")

def register(request):
    if(request.method=="POST"):
        body = json.loads(request.body.decode('utf-8'))
        if(['first_name',"last_name","age","monthly_income","phone_number"] == list(body)): #Verifying body
            body['approved_limit'] = round_to_nearest_lakh(36*body['monthly_income'])
            body['monthly_salary'] = body['monthly_income']
            body.pop('monthly_income')
            try:
                customer = Customer.objects.create(**body)
                return JsonResponse({'customer_id': customer.customer_id, 'name': customer.first_name+" "+customer.last_name, "age":customer.age,"monthly_income":customer.monthly_salary,"approved_limit":customer.approved_limit, "phone_number":customer.phone_number})
            except Exception as e:
                print("error occured while creating customer")
                return JsonResponse({"error":True,"message":e})
        else:
            return JsonResponse({"error":"Missing required body data"})
    else:
        return JsonResponse({"message":"NO valid GET request or this route"})
        
def create_loan(request):
    if(request.method=="POST"):
        body = json.loads(request.body.decode('utf-8'))
        if(['customer_id',"loan_amount","interest_rate","tenure"] == list(body)): #Verifying body
            try:
                customer_id = body['customer_id']
                loan_amount = body['loan_amount']
                tenure = body['tenure']
                interest = body['interest_rate']
                # Verifying customer Id
                customer = Customer.objects.get(customer_id=customer_id)
                if(not customer):
                   return JsonResponse({"error":True,"message":"Customer not found"})
                
                loan_approved = loan_amount < (customer.approved_limit - customer.current_debt)
                if(not loan_approved):
                    message = "Loan amount is greater than limit for this customer by "+str(customer.current_debt + loan_amount - customer.approved_limit)
                    return JsonResponse({"error":True,"message":message})

                customer.current_debt = (customer.current_debt or 0) + loan_amount
                customer.save()
                monthly_installment = round(calculate_monthly_installment(loan_amount,interest,tenure))
                loan = Loan.objects.create(loan_id=customer_id,customer=customer,loan_amount=loan_amount,tenure=tenure,interest_rate=interest,monthly_repayment=monthly_installment,start_date=date.today())
                return JsonResponse({"loan_id":loan.id,"customer_id":customer_id,"loan_approved":loan_approved,"monthly_installment":monthly_installment})
            except Exception as e:
                print("Error occured while adding loan")
                print(e)
                return JsonResponse({"error":True,"message":e})