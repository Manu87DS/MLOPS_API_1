# -*- coding: utf-8 -*-
"""
Created on Fri Dec 31 09:21:33 2021

@author: utilisateur
"""
# uvicorn main2:app --reload
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import pandas as pd
import json
import os
import requests
import random

app = FastAPI()

from fastapi import FastAPI, Response
from fastapi import HTTPException
# from db_questions import DataQuestions

app = FastAPI()
#data = requests.get(csv_url)
#csv_url = "https://dst-de.s3.eu-west-3.amazonaws.com/fastapi_fr/questions.csv"
PATH = os.path.abspath('')
csv_url = os.path.join(PATH, "questions.csv")
    
# Importation of the questions data class
##data = DataQuestions.data

data = pd.read_csv(csv_url)
data = data.fillna('')
# data = data.to_json()

@app.get("/get_data")
def get_data():
    return data                 

@app.get("/get_type_test")
async def get_type_test (data):
    uses = [i for i in data['use'].unique()]
    #uses = list(filter(lambda x: x.get(data['use']) == data['use'].unique(), data)) ## NOK
    return uses

    # https://www.geeksforgeeks.org/lambda-filter-python-examples/ 
        
@app.get("/get_use_test")
async def get_use_test(data):
    """Get all the unique test type in the database.
    """
    uses = [i for i in data.use.unique()]
    return list(uses)

@app.get("/get_subject_test")
async def get_subject_test(use):
    """Get all the unique subjects for a specific test type.
    """
    subjects = [i for i in data.subject[data.use == use].unique()]
    return subjects

@app.get("/get_return_questions")
def return_questions(use, subject, nombre):
    """Returns the questions according to the chosen test type and subjects.
    """
    quest = dict()
    questions = [i for i in data.question[(data.use == use) & (data.subject.isin(subject))]]
    # Shuffle the questions to have a random return for each request.
    random.shuffle(questions)
    for i, v in enumerate(questions[:nombre]):
        quest.update({
            f"Question {i+1}": {
                "question": v,
                "A": data.loc[data.index[data.question == v], "responseA"].item(),
                "B": data.loc[data.index[data.question == v], "responseB"].item(),
                "C": data.loc[data.index[data.question == v], "responseC"].item(),
                # The question D appear only if the value is not empty in the database.
                **({
                    "D": data.loc[data.index[data.question == v], "responseD"].item()
                    } 
                if data.loc[data.index[data.question == v], "responseD"].item() != '' else {})
            }
        })
    return quest

@app.get("/get_add_questions")
def add_question(question):
    """Add the new question in the csv.
    """
    dict_add = {k: [v] for k, v in question.items()}
    df_add = pd.DataFrame(dict_add)
    # Add the new question in the CSV file.
    df_add.to_csv(csv_url, mode="a", index=False, header=False)