###################
# Run This app.py using the following command
# uvicorn app:app --reload
###################
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

class FDEnquiryModel(BaseModel):
    amount: float
    tenor: int

class FDMaturityModel(BaseModel):
    account_id: int
 
app = FastAPI()
 
@app.post("/fdenquiry/")
def fd_enquiry(fdenquirydata: FDEnquiryModel):
    df = pd.read_csv("fd_interest_rates.csv")
    tenor = fdenquirydata.tenor
    print("Tenor is: {}".format(tenor))
    if tenor < 2 or tenor > 360:
        return {
                    "error_msg": "Tenor should be atleast 2 months or at max 360 months!",
                    "status": "ERROR"
                }
    row = df[(df['tenors_start'] <= tenor) & (df['tenor_end'] > tenor)]
    rate = row['interest_rates'].values[0]
    print("Interest Rate: {} for the given tenor.".format(rate))
    invest_amt = fdenquirydata.amount
    print("Investment Amount: {}".format(invest_amt))
    matured_amount = invest_amt * (1 + rate * (1/100) * (1/12))**(tenor)
    print("Matured Amount: {}".format(matured_amount))
    return {
                "Invested Amount": round(float(invest_amt), 2), 
                "matured_amount": round(float(matured_amount), 2),
                "interest_rate": float(rate),
                "status": "SUCCESS"
            }

@app.post("/fdmaturity/")
def fd_maturity(fdmaturitydata: FDMaturityModel):
    df = pd.read_csv("fd_maturity.csv")
    cust_id = fdmaturitydata.account_id
    is_cust_id = any(df["customer_id"] == cust_id)
    if is_cust_id:
        fetched_data = df[df["customer_id"] == cust_id].to_dict('index')
        return {
                    **fetched_data[list(fetched_data.keys())[0]], "status": "SUCCESS"
               }
    else:
        return {
                    "error_msg": "Customer ID: {} does not exists.".format(int(cust_id)),
                    "status": "ERROR"
                }
