import json
from django.db import DatabaseError, IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from core.models import Customer, Loan
from datetime import date, datetime
from django.views.decorators.http import require_POST
from django.core.serializers import serialize
from .pydantic_model import CheckEligibility, CustomerCreate
from pydantic_core import ValidationError
from core.utils import calculate_credit_score, calculate_interest_rate, calculate_monthly_installment, calculate_total_months, round_to_nearest_lakh


def home(request):
    return HttpResponse("API healthy!!")


@require_POST
def register(request):
    try: 
        body = CustomerCreate.model_validate(json.loads(request.body))
    except ValidationError as e:
        print("validation error")
        return JsonResponse({"error":True,"message":str(e)},status=400)
    
    body = dict(body)
    body["approved_limit"] = round_to_nearest_lakh(36 * body["monthly_income"])
    body["monthly_salary"] = body["monthly_income"]
    body.pop("monthly_income")
    
    try:
        customer = Customer.objects.create(**body)
        return JsonResponse(
            {
                "customer_id": customer.customer_id,
                "name": customer.first_name + " " + customer.last_name,
                "age": customer.age,
                "monthly_income": customer.monthly_salary,
                "approved_limit": customer.approved_limit,
                "phone_number": customer.phone_number,
            },status=200
        )
    except IntegrityError as e:
        print("IntegrityError occurred while creating customer")
        return JsonResponse({"error": True, "message": str(e)},status=400)
    except ValidationError as e:
        print("ValidationError occurred while creating customer")
        return JsonResponse({"error": True, "message": str(e)},status=400)
    except Exception as e:
        print("Unexpected error occurred while creating customer")
        return JsonResponse({"error": True, "message": str(e)},status=500)
    
@require_POST
def check_eligibility(request):
    try:
        body = CheckEligibility.model_validate(json.loads(request.body))
    except ValidationError as e:
        return JsonResponse({"error":True,"message":str(e)},status=400)
    
    body = dict(body)
    # Verifying if customer exists
    try:
        customer = Customer.objects.get(customer_id=body['customer_id'])
    except Customer.DoesNotExist:
        return JsonResponse({"error":True,"message":"Customer not found"},status=404)
    except DatabaseError as e:
        print(f"DatabaseError: {e}")
        return JsonResponse({"error": True, "message": "Database error"}, status=500)
        
    approved = True

    # Check if the current debt exceeds the approved limit
    if customer.approved_limit < (customer.current_debt or 0):
        approved = False

    # Retrieve customer's loans and calculate credit score
    loans = customer.loan_set.all()
    credit_score = calculate_credit_score(loans,customer.approved_limit,customer.current_debt,customer.monthly_salary)
    
    # Check if credit score is below a certain threshold
    if(credit_score < 10):
        approved = False

    # Calculate corrected interest rate if approved
    corrected_interest_rate = max(body["interest_rate"],calculate_interest_rate(credit_score,body['interest_rate'])) if approved else None

    return JsonResponse({
        "customer_id":customer.customer_id,
        "approval": approved,
        "interest_rate": body['interest_rate'],
        "corrected_interest_rate":corrected_interest_rate,
        "monthly_installment": calculate_monthly_installment(body['loan_amount'],corrected_interest_rate,body['tenure']) if approved else None
    },status=200)

@require_POST
def create_loan(request):
    loan_eligibility_json = check_eligibility(request)
    approval_response = json.loads(loan_eligibility_json.content.decode('utf-8'))
    if(approval_response.get("error")):
        return loan_eligibility_json
    
    if(not approval_response['approval']):
        return JsonResponse({"loan_approved":False,"message":"Your credit score is not eligible for this loan"})
    
    body = json.loads(request.body.decode("utf-8"))
    customer_id = body["customer_id"]
    loan_amount = body["loan_amount"]
    tenure = body["tenure"]
    interest = approval_response["interest_rate"]
    monthly_installment = approval_response['monthly_installment']
    try:
        loan = Loan.objects.create(
            customer_id=customer_id,
            loan_amount=loan_amount,
            tenure=tenure,
            interest_rate=interest,
            monthly_repayment=monthly_installment,
            start_date=date.today(),
        )
        return JsonResponse({
                "loan_id": loan.id,
                "customer_id": customer_id,
                "loan_approved": approval_response['approval'],
                "monthly_installment": monthly_installment,
            },status=200)
    except IntegrityError as e:
        print("IntegrityError occurred while creating customer")
        return JsonResponse({"error": True, "message": str(e)},status=400)
    except ValidationError as e:
        print("ValidationError occurred while creating customer")
        return JsonResponse({"error": True, "message": str(e)},status=400)
    except Exception as e:
        print("Unexpected error occurred while creating customer")
        return JsonResponse({"error": True, "message": str(e)},status=500)

def view_loan(request, loan_id):
    try:
        loan = Loan.objects.values('id','loan_id','loan_amount','interest_rate','monthly_repayment','tenure','customer_id','customer__first_name','customer__last_name','customer__age').get(id=loan_id)
    except Loan.DoesNotExist:
        try:
            loan = Loan.objects.values('id','loan_id','loan_amount','interest_rate','monthly_repayment','tenure','customer_id','customer__first_name','customer__last_name','customer__age').get(loan_id=loan_id)
        except Loan.DoesNotExist:
            return JsonResponse({"error": True, "message": "Loan with given id doesn't exist"},status=404)
    except DatabaseError as e:
        print(f"DatabaseError: {e}")
        return JsonResponse({"error": True, "message": "Database error"}, status=500)

    loan['customer'] = {"customer_id": loan['customer_id'],
                        "first_name":loan['customer__first_name'],
                        "last_name": loan['customer__last_name'],
                        "age": loan['customer__age']}
    loan['tenure'] = int(loan.get("tenure"))
    loan['loan_id'] = loan['loan_id'] if loan['loan_id'] else loan['id']
    loan.pop("id")
    loan.pop("customer_id")
    loan.pop("customer__first_name")
    loan.pop("customer__last_name")
    loan.pop("customer__age")

    return JsonResponse({"loan":loan},status=200)

def view_customer_loan(request,customer_id):
    def create_respone_loan_dict(loan_obj):
        loan_obj['repayments_left'] = int(loan_obj['tenure']) - int(loan_obj['emis_paid_on_time'] or 0)
        loan_obj['loan_id'] = loan_obj['loan_id'] if loan_obj['loan_id'] else loan_obj['id']
        loan_obj.pop("id")
        loan_obj.pop('emis_paid_on_time')
        loan_obj.pop('tenure')
        return loan_obj    

    try:
        loans = Loan.objects.values("id",'loan_id','loan_amount','interest_rate',"monthly_repayment",'emis_paid_on_time','tenure').filter(customer_id=customer_id)
        loans = list(loans)
        loans = [create_respone_loan_dict(x) for x in loans]
        return JsonResponse({"loans":loans})
    except Loan.DoesNotExist:
        return JsonResponse(
            {"error": True, "message": "Loan with given customer_id doesn't exist"},status=404
        )
