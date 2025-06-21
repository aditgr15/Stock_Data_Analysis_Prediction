from flask import Flask, request, jsonify, render_template_string, redirect, url_for
#from pyngrok import ngrok
import yfinance as yf
import pandas as pd

# initialize the flask app
app=Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"]=True

# html templates
STARTUP_TEMPLATE="""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset='UTF-8'>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title> Welcome to Stock Data Analysis </title>
  <style>
    body {
      font-family: Arial, Sans-serif;
      margin:0 ;
      padding: 0;
      background-color: #f4f4f9;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }
    .container{
      text-align:center;
      background: white;
      padding: 30px;
      border-radius: 8px;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    h1{
      color: #007acc;
    }
    p{
      font-size: 18px;
      margin-bottom: 20px;
    }
    a{
      display: inline-block;
      padding: 10px 20px;
      font-size: 16px;
      color: white;
      background-color: #007acc;
      text-decoration: none;
    }
    a:hover{
      background-color:#005f99;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1> Welcome to stock Data Analysis</h1>
    <p>Analyze Stock trends and performance using real time data visualization and analysis tools</p>
    <a href="/main"> Get Started</a>
  </div>
</body>
</html>
"""

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset='UTF-8'>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Stock Data Analysis </title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
  /*Global Styles*/
  body{
    font-family:Arial,sans-serif;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  header{
    background-color: #4caf50;
    color:  white;
    text-align: center;
    padding: 20px;
  }
  header h1{
    margin: 0;
  }
  main{
    padding: 20px;
    max-width: 1200px;
    margin: auto;
  }
  /*form styles */
  #stock-form{
    display: flex;
    flex-direction:column;
    gap: 10px;
    max-width: 400px;
    margin: auto;
  }
  label{
    font-size: 1.1rem;
  }
  input[type="text"],
  input[type="date"]{
    padding: 10px;
    font-size: 1rem;
    width: 100%;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  button{
    padding: 10px;
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
  }
  button:hover{
    background-color:#45a049
  }
  /*Chart container*/
  #chart-container{
    margin-top: 40px;
    text-align: center;
  }
  canvas{
    max-width: 100%;
    height: auto;
  }
  /*stats*/
  #stats{
    margin-top: 30px;
    text-align: center;
    font-size: 1.1rem;
  }
  /*responsive design*/
  @media screen and (max-width: 760px){
    main{
      padding:10px;
    }
    #stock-form{
      max-width:100%;
    }
    button{
      width: 100%;
    }
  }
  @media-screen and (max-width:480px){
    header{
      padding: 10px;
    }
    header h1{
      font-size: 1.5rem;
    }
    label{
      font-size: 1rem;
    }
    input[type="text"],
    input[type="date"],
    button{
      font-size: 1rem;
    }
    #stats{
      font-size: 1rem;
    }
  }
  #stats h3{
    margin-top: 20px;
    color: #333;
  }
  </style>
</head>
<body>
  <header>
    <h1> Stock Data Analysis</h1>
    <p> Analyze stock trends with real time data</p>
  </header>
  <main>
    <form id="stock-form">
      <label for="ticker">Stock Ticker:</label>
      <input type="text" id="ticker" name="ticker" required>
      <label for="start-date">Start date:</label>
      <input type="date" id="start-date" name="start-date" required>
      <label for="end-date">End date:</label>
      <input type="date" id="end-date" name="end-date" required>
      <button type="button" onclick="fetchStockData()"> Fetch Data </button>
    </form>
    <div id="chart-container">
      <canvas id="stock-chart"></canvas>
    </div>
    <div id="stats"></div>
  </main>
  <script>
    async function fetchStockData(){
      const ticker= document.getElementById("ticker").value;
      const startDate= document.getElementById("start-date").value;
      const endDate= document.getElementById("end-date").value;

      const response= await fetch(`${window.location.origin}/api/stocks?ticker=${ticker}&start=${startDate}&end=${endDate}`);
      const data=await response.json();
      console.log(data);

      if (data.error){
        alert(data.error);
        return;
      }
      const stats=document.getElementById("stats");
      stats.innerHTML=`
        <p>Average Price:${data.summary.average.toFixed(2)}</p>
        <p>Highest Price:${data.summary.highest.toFixed(2)}</p>
        <p>Lowest Price:${data.summary.lowest.toFixed(2)}</p>
        <p>Average Volume:${data.summary.volume_avg.toFixed(2)}</p>
      `;

      const forecastResponse=await fetch(`${window.location.origin}/api/forecast?ticker=${ticker}&start=${startDate}&end=${endDate}`);
      const forecastData=await forecastResponse.json();
      console.log(forecastData);

      if (forecastData.error){
        alert(forecastData.error);
        return;
      }
      let allDates=data.dates;
      let allPrices=data.prices;

      if (!forecastData.error){
        const forecastDates=forecastData.forecast_dates;
        const forecastPrices=forecastData.forecast;
        allDates=allDates.concat(forecastDates);
        allPrices=allPrices.concat(forecastPrices);
        const forecastDiv=document.createElement('div');
        forecastDiv.innerHTML=`<h3> 5-Day forecast(ARIMAS):</h3><ul>`+
          forecastData.forecast.map((price,idx)=>`<li>${forecastDates[idx]}: ${price.toFixed(2)}</li>`).join("")+
          `</ul>`;
          stats.appendChild(forecastDiv)
      }
      const ctx=document.getElementById("stock-chart").getContext("2d");
      new Chart(ctx,{
        type:"line",
        data:{
          labels:allDates,
          datasets:[
            {
              label:"Historical Price",
              data:data.prices,
              borderColor:"rgba(75,192,192,1)",
              borderWidth:2,
              fill:false
            },
            {
              label:"Forecasted Price",
              data:Array(data.prices.length).fill(null).concat(forecastData.forecast),
              borderColor:"rgba(255,99,132,1)",
              borderDash:[5,5],
              borderWidth:2,
              fill:false
            }
          ]
        },
        options:{
          responsive:true,
          scales:{
            x:{title:{display:true,text:"Date"}},
            y:{title:{display:true,text:"Price"}}
          }
        }
      });
    }
  </script>
</body>
</html>


'''

@app.route("/api/stocks",methods=["GET"])
def get_stock_data():
  ticker=request.args.get("ticker")
  start_date=request.args.get("start")
  end_date=request.args.get("end")
  #!fetch stock data
  stock=yf.download(ticker,start=start_date,end=end_date)
  # Handle case when no data is found
  if stock.empty:
    return jsonify({"error":"no data found"}),404
  #debugging: check the columns and types of stock data frames
  print(f"columns in stock dataframes:{stock.columns}")
  print(f"datatype of close:{type(stock[('Close',ticker)])}")
  #convert the index(date)to a list of strings
  stock["Date"]=stock.index.strftime("%Y-%m-%d")
  # Convert series to list
  dates_list=stock["Date"].tolist()
  prices_list=stock[("Close",ticker)].tolist()
  print(f"First few rows of date:{dates_list[:5]}")
  print(f"First few rows of close:{prices_list[:5]}")
  try:
    #Construct the response
    response={
        "dates":dates_list,
        "prices":prices_list,
        "summary":{
            "average": stock[("Close",ticker)].mean(),
            "highest": stock[("Close",ticker)].max(),
            "lowest": stock[("Close",ticker)].min(),
            "volume_avg": stock[("Volume",ticker)].mean(),

        }
    }
    return jsonify(response)
  except Exception as e:
    return jsonify({"error":str(e)}),500

@app.route("/")
def startup_page():
  return render_template_string(STARTUP_TEMPLATE)

@app.route("/main")
def main_page():
  return render_template_string(HTML_TEMPLATE)

from pandas.tseries.offsets import BDay
from statsmodels.tsa.arima.model import ARIMA

@app.route("/api/forecast",methods=["GET"])
def forecast_stock():
  ticker=request.args.get("ticker")
  start_date=request.args.get("start")
  end_date=request.args.get("end")
  stock=yf.download(ticker,start=start_date,end=end_date)
  if stock.empty:
    return jsonify({"error":"no data found"}),404
  else:
    print("stock\n",stock)
  try:
    close_prices=stock["Close"]
    print("Close Price\n",close_prices)
    last_date=close_prices.index[-1]

    model=ARIMA(close_prices,order=(5,1,0))
    model_fit=model.fit()
    forecast=model_fit.forecast(steps=5)

    #Generate 5 business dates after last availible date
    future_dates=pd.date_range(last_date+BDay(1),periods=5).strftime("%Y-%m-%d").tolist()
    return jsonify({
        "forecast":forecast.tolist(),
        "forecast_dates":future_dates
    })
  except Exception as e:
    return jsonify({"error":str(e)}),500

if __name__ == '__main__':
    app.run(port=8000)
