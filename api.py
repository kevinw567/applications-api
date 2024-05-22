from fastapi import FastAPI
from pydantic import BaseModel
import gspread
import pandas as pd
import numpy as np
from typing import Literal



class Application(BaseModel):
    company: str
    position: str
    remote: Literal['Yes', 'No', 'Hybrid']
    location: str | None = None
    date: str | None = None
    platform: str
    link: str | None = None
    status: str
    result: str | None = None
    comments: str | None


app = FastAPI()

gc = gspread.service_account(filename = './sheets-api-421004-e504ab6f2753.json')
sheet = gc.open("Applications").get_worksheet(1)

header_row = sheet.row_values(1)[:10]

@app.get("/companies/{company_name}")
def search_by_company(company_name: str):
    """
    Get all records for a specific company name

    Args:
        company_name (str): the name of the company to search for

    Returns:
        list: a list of the matching records and their details
    """
    first_col = sheet.col_values(1)
    matches = []
    for row in range(len(first_col) - 1):
        if first_col[row].lower() == company_name.lower():
            matching = sheet.get(f"{row}0:{row}10")
            res = {}
            for i in range(9):
                res[header_row[i]] = sheet.cell(row + 1, i + 1).value
                
            matches.append(res)
        
    return {
        "message": f"Applications to {company_name}",
        "count": f"{len(matches)}",
        "results": matches 
    }


@app.get("/all-companies")
def get_all_companies():
    """
    Get a list of all the companies and the number of times they occur in the spreadsheet

    Returns:
        dict: a dict of all companies and the number of occurances 
    """
    companies = sheet.col_values(1)
    results = {}
    for company in companies:
        if company in results: results[company] += 1
        else: results[company] = 1
        
    return {
        'count': f"{len(results.keys())}",
        'results': results
    }
    
    
@app.get("/full_sheet")
def get_all():
    """
    Get all values from the entire spreadsheet

    Returns:
        list: all items and their details in the spreadsheet
    """
    all = sheet.get_all_records(expected_headers=header_row)
    return { 'results': all }


@app.post("/new_application/")
async def post(application: Application):
    data = application.dict() 
    next_row = len(sheet.col_values(1)) + 1
    row = np.array([list(data.values())])
    print(row)
    sheet.update(list(row.tolist()), f"A{next_row}" )        
    return {
        'data': data,
        'new_row': next_row
    }