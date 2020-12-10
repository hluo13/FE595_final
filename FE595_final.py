from flask import Flask, request, render_template, jsonify, Response
from pandas import DataFrame
import matplotlib as plt
import matplotlib.pyplot as plot
import numpy as np
import pandas as pd
import pandas_datareader as pdr

app = Flask(__name__)


def stock_analyze():
    input_text = request.form['text1']
    company_list = input_text.split(",")
    df=pd.DataFrame()
    for i in company_list:
        df[i]=pdr.DataReader(i,data_source='yahoo',start='2015/1/1',end='2020/12/6')['Close']#get the close price
        
        d42=pd.DataFrame()
        d252=pd.DataFrame()
        d42_252=pd.DataFrame()
        
        signal=pd.DataFrame()
        market=pd.DataFrame()
        strategy=pd.DataFrame()
        
    for i in company_list:
        d42[i]=np.round(df[i].rolling(20).mean(),2)#42days moving average
        d252[i]=np.round(df[i].rolling(252).mean(),2)#252days moving average
        d42.index=d252.index
        d42_252[i]=d42[i]-d252[i]#get the lag
        
    for i in company_list:
        SD=5#we set the profit be 5, once the price lower than 5 the signal will be zero.
        signal[i]=np.where(d42_252[i]>SD,1,np.where(d42_252[i]<-SD,-1,0))#signal for buying or 
        market[i]=np.log(df[i]/df[i].shift(1))#Bottom pool stock yield
        signal.index=market.index
        strategy[i]=signal[i].shift(1)*market[i]#Bottom pool owning stock yield
        strategy['strategy']=strategy.sum(axis=1)#Calculate the total return on holdings
        
    strategy.tail()
    strategy['sp500']=pdr.DataReader('^GSPC',data_source='yahoo',start='2015/1/1',end='2020/12/6')['Close']#Benchmark closing price
    strategy['market']=np.log(strategy['sp500']/strategy['sp500'].shift(1))#Calculate market returns
    strategy[['Market','Strategy']]=strategy[['market','strategy']].cumsum().apply(np.exp)#Calculate the total holding return of market and strategy

    result=['\n The market holding final return:%s'%strategy['Market'][-1:],
            '\n The strategy holding final return:%s'%strategy['Strategy'][-1:],
            '\n Average market return：%s'%strategy['Market'].mean(),
            '\n Average strategy return：%s'%strategy['Strategy'].mean(),
            '\n Maximum strategy return：%s'%strategy['Strategy'].max(),
            '\n Maximum market return：%s'%strategy['Market'].max(),
            '\n Market maximum pullback in one day：%s'%strategy['market'].min(),
            '\n Strategy maximum pullback in one day：%s'%strategy['strategy'].min(),
            '\n Strategy volatility：%s'%strategy['Strategy'].std(),
            '\n Market volatility：%s'%strategy['Market'].std()]
    return result


@app.route('/')
def home():
    return render_template('request.html')


@app.route('/join', methods=['GET', 'POST'])
def my_form_post():
    text2 = request.form['text2']
    if text2.lower() == 'analyze':
        combine = stock_analyze()
        result = {"output": combine}
        result = {str(key): value for key, value in result.items()}
        return jsonify(result=result)
    else:
        print("400 Bad request")
        return jsonify(result="Not Found"), 400



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
    #app.run()
