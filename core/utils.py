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