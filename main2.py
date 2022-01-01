# -*- coding: utf-8 -*-
"""
Created on Fri Dec 31 09:21:33 2021

@author: utilisateur
"""
# uvicorn main2:app --reload
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
app = FastAPI()
import pandas as pd
import json
import os
import requests
import random

#data = pd. read_csv(csv_url)
#data = data.fillna('')
#data = requests.get(csv_url)

# csv_url = "https://dst-de.s3.eu-west-3.amazonaws.com/fastapi_fr/questions.csv"

PATH = os.path.abspath('')
csv_url = os.path.join(PATH, "questions.csv")

class DataQuestions:
    """read database"""
    
    def __init__(self):
        """Initiate csv data 
        
        Attribute
        ---------
        data : DataFrame CSV file.
        """
        self.data = pd.read_csv(csv_url)
        self.data = self.data.fillna('')
    
    @property #In Python, property() is a built-in function that creates and returns a property object. The syntax of this function i
    def data(self):
        """Return dataframe."""
        return self.data
    
# Importation of the questions data.
data = DataQuestions().data

#@app.get("/get_data")
#def get_data():
#    return data                 

##### l'utilisateur doit pouvoir choisir un type de test (use) ainsi qu'une ou plusieurs catégories (subject)
##### De plus, l'application peut produire des QCMs de 5, 10 ou 20 questions

@app.get("/get_type_test")
async def get_type_test (data):
    uses = [i for i in data['use'].unique()]
    return uses
        
@app.get("/get_use_test")
async def get_use_test(data):
    """Get all the unique test type in the database.
    Return
    ------
    uses : list
        A list with all the unique test type in the database.
    """
    uses = [i for i in data.use.unique()]
    return uses

@app.get("/get_subject_test")
async def get_subject_test(use):
    """Get all the unique subjects for a specific test type.
    
    Return
    ------
    subjects : list
        A list with all the unique subject for a specific test type  in the database.
    """
    subjects = [i for i in data.subject[data.use == use].unique()]
    return subjects

def return_questions(use, subject, nombre):
    """Returns the questions according to the chosen test type and subjects.
    
    Parameters
    ----------
    use : str
        The test type  in the API request. 
    subjects : list
        The list of subjects in the API request.
    
    Return
    ------
    quest : dict
        A dictionnary with the questions and the answers to choose.
    """
    quest = dict()
    questions = [q for q in data.question[(data.use == use) & (data.subject.isin(subject))]]
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


def add_question(question):
    """Add the new question in the csv.
    
    Paramater
    ---------
    question : dict
        A dictionnary with the elements to add
    """
    dict_add = {k: [v] for k, v in question.items()}
    df_add = pd.DataFrame(dict_add)
    # Add the new question in the CSV file.
    df_add.to_csv(csv_url, mode="a", index=False, header=False)