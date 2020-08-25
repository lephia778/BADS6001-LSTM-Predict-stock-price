#Import Library
import json
import os
from random import randint
from flask import Flask
from flask import request
from flask import make_response

#Import Function
import G000function
import G002function
#........................................

# Default syntax for Flask.
app = Flask(__name__)
@app.route('/', methods=['POST']) #Using methods = ['post']
#........................................

# Main Function
def MainFunction():

    #Getting Data
    question_from_dailogflow_raw = request.get_json(silent=True, force=True)

    #Answering
    answer_from_bot = generating_answer(question_from_dailogflow_raw)
    answer_from_bot = json.dumps(answer_from_bot, indent=4) #Formatting JSON
    r = make_response(answer_from_bot)
    r.headers['Content-Type'] = 'application/json' #Setting Content Type

    return r

#........................................

def generating_answer(question_from_dailogflow_dict):
 
    debug_print(question_from_dailogflow_dict)
    
    intent_group_question_str = question_from_dailogflow_dict["queryResult"]["intent"]["displayName"] # Name of intent group.

    #Select function for processing question
    if intent_group_question_str == 'กินอะไรดี':
        answer_str = G000function.menu_recormentation()
    elif intent_group_question_str == 'BMI - Confirmed W and H': 
        answer_str = G000function.BMI_calculation(question_from_dailogflow_dict)
    elif intent_group_question_str == 'Predict Stock - Ask Stock Name':
        answer_str = G002function.predict_stockprice(question_from_dailogflow_dict)
    else: answer_str = "ผมไม่เข้าใจ คุณต้องการอะไร"
    
    answer_from_bot = {"fulfillmentText": answer_str}

    return answer_from_bot

#Function for debuging.
def debug_print(question_dict):
    print('\n\n')
    print(json.dumps(question_dict, indent=4 ,ensure_ascii=False))
    print('\n\n')
#........................................




@app.route('/BatchAnalytic') #Using methods = ['post']

def Batch():
    G002function.analytic_stock()
    return "200"



# Default syntax for Flask.
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0', threaded=True)
#........................................