from datetime import datetime, date

def round_to_nearest_lakh(number):
    return round(number / 100000) * 100000

def calculate_monthly_installment(principal, annual_interest_rate, tenure_in_months):
    monthly_interest_rate = annual_interest_rate / 12 / 100

    # Calculate the monthly installment using the loan payment formula
    monthly_installment = (
        principal
        * monthly_interest_rate
        * ((1 + monthly_interest_rate) ** tenure_in_months)
    ) / (((1 + monthly_interest_rate) ** tenure_in_months) - 1)

    return monthly_installment

def calculate_credit_score(loans,approved_limit,current_debt,monthly_salary):
    total_monthly_emi = 0
    total_loans = len(loans)
    total_current_year_loans = 0
    total_emis_till_date=0
    total_emis_on_time=0
    for loan in loans:
        total_monthly_emi += loan.monthly_repayment
        total_emis_till_date+= calculate_total_months(loan.start_date)
        total_emis_on_time+=(loan.emis_paid_on_time or 0)
        if(loan.start_date.year == datetime.now().year):
            total_current_year_loans+=1

    if(total_monthly_emi > (monthly_salary/2)):
        print("monthly emi too much")
        return 0

    if(total_loans and total_emis_till_date):
        total_on_time_percentage = min(100,(total_emis_on_time/total_emis_till_date)*100)
    else:
        total_on_time_percentage = 100
    # Assuming weights for different variables
    weight_past_loans_on_time=0.3
    weight_loans_taken=0.2
    weight_total_current_year_loans = 0.3
    weight_loan_approved_volume = 0.2

    credit_score = (weight_past_loans_on_time * (total_on_time_percentage/100) + # past_loans_on_time value in percentage
                    weight_loans_taken * (2/(2 + total_loans)) + 
                    weight_total_current_year_loans * (2/(2+total_current_year_loans)) + 
                    weight_loan_approved_volume * ((approved_limit - (current_debt or 0))/approved_limit)
    ) * 100

    return credit_score


def calculate_total_months(previous_date):
    today = datetime.now()
    
    # Calculate the total number of months
    total_months = (today.year - previous_date.year) * 12 + today.month - previous_date.month
    
    # Adjust for cases where the day of the month in today is smaller than the day in the previous_date
    if today.day < previous_date.day:
        total_months -= 1

    return total_months

def calculate_interest_rate(credit_score,interest_rate):
    if(credit_score > 50):
        return interest_rate
    elif(credit_score > 30):
        return 12
    elif(credit_score >= 10):
        return 16
    else:
        return None