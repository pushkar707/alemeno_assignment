import json
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from core.models import Customer, Loan
from datetime import date, datetime
from django.views.decorators.http import require_POST
from django.core.serializers import serialize
from .pydantic_model import CheckEligibility
from pydantic_core import ValidationError
from core.utils import calculate_credit_score, calculate_interest_rate, calculate_monthly_installment, calculate_total_months, round_to_nearest_lakh


def home(request):
    return HttpResponse("API healthy!!")


@require_POST
def register(request):
    body = json.loads(request.body.decode("utf-8"))
    if ["first_name", "last_name", "age", "monthly_income", "phone_number"] == list(
        body
    ):  # Verifying body
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
                }
            )
        except Exception as e:
            print("error occured while creating customer")
            return JsonResponse({"error": True, "message": e})
    else:
        return JsonResponse({"error": "Missing required body data"})

@require_POST
def check_eligibility(request):
    try:
        body = CheckEligibility.model_validate(json.loads(request.body))
    except ValidationError as e:
        return JsonResponse({"error":True,"message":e})
    
    body = dict(body)
    try:
        customer = Customer.objects.get(customer_id=body['customer_id'])
    except Customer.DoesNotExist:
        return JsonResponse({"error":True,"message":"Customer not found"})
    
    approved = True

    if customer.approved_limit < (customer.current_debt or 0):
        message = ("You already have loans above the approved limit")
        approved = False

    loans = customer.loan_set.all()
    credit_score = calculate_credit_score(loans,customer.approved_limit,customer.current_debt,customer.monthly_salary)
    if(credit_score < 10):
        approved = False
    corrected_interest_rate = max(body["interest_rate"],calculate_interest_rate(credit_score,body['interest_rate'])) if approved else None
    print(credit_score, corrected_interest_rate)
    return JsonResponse({
        "customer_id":customer.customer_id,
        "approval": approved,
        "interest_rate": body['interest_rate'],
        "corrected_interest_rate":corrected_interest_rate,
        "monthly_installment": calculate_monthly_installment(body['loan_amount'],corrected_interest_rate,body['tenure']) if approved else None
    })

@require_POST
def create_loan(request):
    body = json.loads(request.body.decode("utf-8"))
    if ["customer_id", "loan_amount", "interest_rate", "tenure"] == list(
        body
    ):  # Verifying body
        customer_id = body["customer_id"]
        loan_amount = body["loan_amount"]
        tenure = body["tenure"]
        interest = body["interest_rate"]
        try:
            # Verifying customer Id
            customer = Customer.objects.get(customer_id=customer_id)
            if not customer:
                return JsonResponse({"error": True, "message": "Customer not found"})

            # Checking if loan amount is within approval
            loan_approved = loan_amount < (
                customer.approved_limit - (customer.current_debt or 0)
            )
            if not loan_approved:
                message = (
                    "Loan amount is greater than limit for this customer by "
                    + str(customer.current_debt + loan_amount - customer.approved_limit)
                )
                return JsonResponse({"error": True, "message": message})

            # Editing customer's current debt
            customer.current_debt = (customer.current_debt or 0) + loan_amount
            customer.save()
            monthly_installment = round(
                calculate_monthly_installment(loan_amount, interest, tenure)
            )
            loan = Loan.objects.create(
                loan_id=customer_id,
                customer=customer,
                loan_amount=loan_amount,
                tenure=tenure,
                interest_rate=interest,
                monthly_repayment=monthly_installment,
                start_date=date.today(),
            )
            return JsonResponse(
                {
                    "loan_id": loan.id,
                    "customer_id": customer_id,
                    "loan_approved": loan_approved,
                    "monthly_installment": monthly_installment,
                }
            )
        except Exception as e:
            print("Error occured while adding loan")
            print(e)
            return JsonResponse({"error": True, "message": e})
    else:
        pass

def view_loan(request, loan_id):
    try:
        loan = Loan.objects.filter(id=loan_id).values('id','loan_id','loan_amount','interest_rate','monthly_repayment','tenure','customer_id','customer__first_name','customer__last_name','customer__age')
    except Loan.DoesNotExist:
        try:
            loan = Loan.objects.filter(loan_id=loan_id).values('id','loan_id','loan_amount','interest_rate','monthly_repayment','tenure','customer_id','customer__first_name','customer__last_name','customer__age')
        except Loan.DoesNotExist:
            return JsonResponse(
                {"error": True, "message": "Loan with given id doesn't exist"}
            )
    loan = list(loan)[0]
    loan['customer'] = {"customer_id": loan['customer_id'],
                        "first_name":loan['customer__first_name'],
                        "last_name": loan['customer__last_name'],
                        "age": loan['customer__age']}
    loan.pop("customer_id")
    loan.pop("customer__first_name")
    loan.pop("customer__last_name")
    loan.pop("customer__age")
    return JsonResponse({"loan":loan})

def view_customer_loan(request,customer_id):
    def create_respone_loan_dict(loan_obj):
        loan_obj['repayments_left'] = int(loan_obj['tenure']) - int(loan_obj['emis_paid_on_time'] or 0)
        loan_obj.pop('emis_paid_on_time')
        loan_obj.pop('tenure')
        return loan_obj
    

    try:
        loans = Loan.objects.filter(customer_id=customer_id).values('loan_id','loan_amount','interest_rate',"monthly_repayment",'emis_paid_on_time','tenure')
        loans = list(loans)
        loans = [create_respone_loan_dict(x) for x in loans]
        return JsonResponse({"loans":loans})
    except Loan.DoesNotExist:
        return JsonResponse(
            {"error": True, "message": "Loan with given customer_id doesn't exist"}
        )
