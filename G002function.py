import csv
import numpy as np
import pandas as pd
import pandas_datareader as pdr
import datetime
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense, LSTM


def predict_stockprice(respond_dict):

    # get input parameter
    stock_name = str(respond_dict["queryResult"]["parameters"]["Stock_name"]).upper()
    file = 'predict stock price.csv'
    data = pd.read_csv(file, sep=',', header=0, index_col='Name')
    predict_price = data.loc[stock_name, 'Predict Price']
    latest_price = data.loc[stock_name, 'Latest Price']
    change = round((predict_price - latest_price) / (latest_price) * 100 ,2)
    answer = '''{} \nราคาปิดล่าสุด {} บาท \nคาดว่าจะมีราคาปิดเย็นนี้ {} บาท \nมีการเปลี่ยนแปลง {}%'''.format(stock_name, latest_price, predict_price, change)
    return answer


def analytic_stock():
    # variable for getting stock data
    stock_list = ['ADVANC', 'AOT', 'BANPU', 'BBL', 'BDMS', 'BEM', 'BGRIM' ,'BH', 'BJC', 'BPP',
                  'BTS', 'CENTEL', 'CPALL' ,'CPF', 'CPN', 'DELTA', 'DTAC', 'EA', 'EGCO', 'GLOBAL',
                  'GLOW', 'GPSC', 'GULF', 'HMPRO', 'INTUCH', 'IRPC', 'IVL', 'KBANK', 'KKP','KTB',
                   'KTC', 'LH' ,'MINT', 'MTC', 'PTT', 'PTTEP', 'PTTGC', 'RATCH', 'ROBINS', 'SCB',
                   'SCC', 'SPRC', 'TCAP', 'TISCO', 'TMB', 'TOA', 'TOP', 'TRUE', 'TU', 'WHA']
    stock_data = []
    startdate = datetime.date.today() - datetime.timedelta(150)
    enddate = datetime.date.today() - datetime.timedelta(1)

    # get stock data from yahoo  
    for quote in stock_list:
        stock_data.append(pdr.get_data_yahoo(f'{quote}.BK', 
                                                start=startdate, end=enddate))

    # choose last 90 days and drop column 'Close' (unused)
    for i in range(len(stock_data)):
        stock_data[i] = stock_data[i].tail(90)
        stock_data[i].drop('Close', axis=1, inplace=True)

    # function for preprocess multivariate time series
    def series_to_supervised(data, dropnan=True,feature_name=None):
        no_of_vars = data.shape[1]
        df = pd.DataFrame(data)
        cols = list()
        names = list()
        
        # 29 previous days shift + last day for multivariate feature
        for i in range(29, 0, -1):
            cols.append(df.shift(i))
            for j in range(no_of_vars):
                names += [f'{feature_name[j]}(t-{i})']
        cols.append(df.shift(0))
        for j in range(no_of_vars):
            names += [f'{feature_name[j]}(t)']
                
        # 1 forward day shift to cols list for output data
        cols.append(df.shift(-1))
        for j in range(no_of_vars):
            names += [f'{feature_name[j]}(t+1)']
        
            
        # put it all together
        concat_df = pd.concat(cols, axis=1)
        concat_df.columns = names
        
        # drop unused 29 rows and unused 4 columns 
        concat_df.drop(range(0,29), inplace=True)
        concat_df.drop(['High(t+1)','Low(t+1)', 'Open(t+1)','Volume(t+1)'],axis=1,inplace=True)
        return concat_df

    # loop predict stock price
    dict_stock = dict()
    for no_of_stock in range(len(stock_list)):

        dataset = stock_data[no_of_stock].copy()
        # get lastest adjust close value for add dict_stock after predict
        latest_adjusted_close = round(dataset.iat[-1,-1],2)

        # create min and max variable 'Adj Close' for convert back after predict
        max_adj_close = max(dataset['Adj Close'])
        min_adj_close = min(dataset['Adj Close'])

        # scale dataset to [-1, 1]
        for col in dataset.columns:
            dataset[col] = (dataset[col] - dataset[col].min())/(dataset[col].max()-dataset[col].min())

        # transform data by preprocess function
        reframed = series_to_supervised(dataset.values, feature_name=stock_data[no_of_stock].columns)
        
        # split into train and predict sets
        train = reframed.values[:-1]
        predict = reframed.values[-1:]
        
        # split Into X(input) and y(output)
        train_X = train[:,:-1]  
        train_y = train[:,-1:]
        predict_X  = predict[:,:-1]
        
        # reshape input to be 3D [samples, time step, features]
        train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
        predict_X = predict_X.reshape((predict.shape[0], 1, predict_X.shape[1]))
            
        # prepare and fit model
        model = Sequential()
        model.add(LSTM(50, input_shape=(train_X.shape[1], train_X.shape[2])))
        model.add(Dense(1))  # ขนาดของ output
        model.compile(loss='mse', optimizer='adam') 
        model.fit(train_X, train_y, epochs=50, verbose=2, shuffle=False)

        # make a prediction
        predict_price = model.predict(predict_X)
        predict_X = predict_X.reshape((predict_X.shape[0], predict_X.shape[2]))

        # inverse scaling data back to original scale
        predict_price = predict_price*(max_adj_close-min_adj_close)+min_adj_close
                                
        # round and add predict stock price to dict_stock
        predict_price = predict_price[0][0]
        if predict_price < 2:
            predict_price = round(predict_price * 100)/100
        elif 2 <= predict_price < 5:
            predict_price = round(predict_price * 50)/50
        elif 5 <= predict_price < 10:
            predict_price = round(predict_price * 20)/20
        elif 10 <= predict_price < 25:
            predict_price = round(predict_price * 10)/10
        elif 25 <= predict_price < 100:
            predict_price = round(predict_price * 4)/4
        elif 100 <= predict_price < 200:
            predict_price = round(predict_price * 2)/2
        elif 200 <= predict_price < 400:
            predict_price = round(predict_price)
        else:
            predict_price = round(predict_price * 0.5)/0.5
        
        dict_stock[stock_list[no_of_stock]] = latest_adjusted_close, predict_price

    # write dict to csv file
    with open('predict stock price.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(('Name', 'Latest Price','Predict Price'))
        for key, value in dict_stock.items():
            writer.writerow([key, value[0], value[1]])
