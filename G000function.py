#Import Library

from random import randint
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

#Fire Base Admin
cred = credentials.Certificate("tutorial-chat-bot-firebase-adminsdk-tz7a1-59f06a345a.json")
firebase_admin.initialize_app(cred)

#User defind function
def menu_recormentation(): #Function for recommending menu
    #----Additional from previous file----
    database_ref = firestore.client().document('Food/Menu_List')
    database_dict = database_ref.get().to_dict()
    database_list = list(database_dict.values())
    ran_menu = randint(0, len(database_list)-1)
    menu_name = database_list[ran_menu]
    #-------------------------------------
    answer_function = menu_name + ' สิ น่ากินนะ'
    return answer_function

def BMI_calculation(respond_dict): #Function for calculating BMI

    #Getting Weight and Height
    weight_kg = float(respond_dict["queryResult"]["outputContexts"][2]["parameters"]["Weight.original"])
    height_cm = float(respond_dict["queryResult"]["outputContexts"][2]["parameters"]["Height.original"])
    
    #Calculating BMI
    BMI = weight_kg/(height_cm/100)**2
    if BMI < 18.5 :
        answer_function = "คุณผอมเกินไปนะ"
    elif 18.5 <= BMI < 23.0:
        answer_function = "คุณมีนำ้หนักปกติ"
    elif 23.0 <= BMI < 25.0:
        answer_function = "คุณมีนำ้หนักเกิน"
    elif 25.0 <= BMI < 30:
        answer_function = "คุณอ้วน"
    else :
        answer_function = "คุณอ้วนมาก"
    return answer_function

#........................................

