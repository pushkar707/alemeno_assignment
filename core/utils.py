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

def calculate_credit_score(past_loans_on_time,loans_taken,total_current_year_loans,current_debt, approved_limit):
    # Assuming weights for different variables
    weight_past_loans_on_time=0.3
    weight_loans_taken=0.3
    weight_total_current_year_loans = 0.2
    weight_loan_approved_volume = 0.2

    credit_score = (weight_past_loans_on_time * (past_loans_on_time/100) + # past_loans_on_time value in percentage
                    weight_loans_taken * (2/(2 + loans_taken)) + 
                    weight_total_current_year_loans * (2/2+total_current_year_loans) + 
                    weight_loan_approved_volume * ((approved_limit - current_debt)/approved_limit)
    ) * 100 

    print(credit_score)
    credit_score = max(0, min(100, credit_score)) # this is only for unapplicable cases like passing negative values

    return credit_score


