import streamlit as st
import yfinance as yf
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="Pairs Trading Backtest",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Function to calculate pairs trading strategy
def Pairs(Ticker1, Ticker2, years, UB_entry, LB_entry, UB_exit, LB_exit, Amount_Per_Pair=10000, Transaction_Cost=0):

    # Validating Parameters
    Ticker1 = str(Ticker1)
    Ticker2 = str(Ticker2)
    UB_entry = float(UB_entry)
    LB_entry = float(LB_entry)
    UB_exit = float(UB_exit)
    LB_exit = float(LB_exit)
    Amount_Per_Pair = float(Amount_Per_Pair)

    # Downloading Data
    Ticker1Data = yf.download(Ticker1, dt.date.today() - dt.timedelta(days=365 * int(years)), dt.date.today())
    Ticker2Data = yf.download(Ticker2, dt.date.today() - dt.timedelta(days=365 * int(years)), dt.date.today())

    # Ticker validation
    if Ticker1Data.empty or Ticker2Data.empty:
        return None
    
    # Setting up DataFrame
    df = pd.DataFrame(columns=['T1 Close', 'T2 Close', 'Price Ratio', 'Z-Score', 'Signal', 'T1 Trade', 'T2 Trade', 
                               'T1 Position', 'T2 Position', 'Transaction Cost', 'T1 Trading Cash', 
                               'T2 Trading Cash', 'Total Trading Cash', 'T1 M2M', 'T2 M2M', 'Total M2M', 'Pnl'])

    # Cleaning up stock Data & placing it into df
    df['T1 Close'] = Ticker1Data['Adj Close']
    df['T2 Close'] = Ticker2Data['Adj Close']
    
    # Calculating Price Ratio
    df['Price Ratio'] = df['T1 Close'] / df['T2 Close']

    # Calculating mean and standard deviation for the entire dataset
    mean_ratio = df['Price Ratio'].mean()
    std_ratio = df['Price Ratio'].std()

    # Calculating Z-Score based on the entire dataset
    df['Z-Score'] = (df['Price Ratio'] - mean_ratio) / std_ratio

    # Calculating Signal based on Z-Score
    def Calculate_Signal(row):
        if row['Z-Score'] >= UB_entry:
            row['Signal'] = 'Short Pair'
        elif row['Z-Score'] <= -LB_entry:
            row['Signal'] = 'Long Pair'
        else:
            row['Signal'] = 'Flat Pair'
        return row
    
    df = df.apply(Calculate_Signal, axis=1)

    # Populating row 0 of Positions & Trade
    if df['Signal'].iloc[0] == 'Short Pair':
        df.loc[df.index[0], 'T1 Position'] = -round((Amount_Per_Pair/2)/df.loc[df.index[0], 'T1 Close'])
        df.loc[df.index[0], 'T2 Position'] = round((Amount_Per_Pair/2)/df.loc[df.index[0], 'T2 Close'])
    elif df['Signal'].iloc[0] == 'Long Pair':
        df.loc[df.index[0], 'T1 Position'] = round((Amount_Per_Pair/2)/df.loc[df.index[0], 'T1 Close'])
        df.loc[df.index[0], 'T2 Position'] = -round((Amount_Per_Pair/2)/df.loc[df.index[0], 'T2 Close'])
    else:
        df.loc[df.index[0], 'T1 Position'] = 0
        df.loc[df.index[0], 'T2 Position'] = 0
    
    df.loc[df.index[0], 'T1 Trade'] = df.loc[df.index[0], 'T1 Position']
    df.loc[df.index[0], 'T2 Trade'] = df.loc[df.index[0], 'T2 Position']

    # Populating the rest of rows for T1 Position
    for i in range(1, len(df)):
        if df['T1 Position'].iloc[i-1] != 0:
            if df['Signal'].iloc[i] == 'Short Pair':
                df.loc[df.index[i], 'T1 Position'] = df['T1 Position'].iloc[i-1] if df['T1 Position'].iloc[i-1] < 0 else -round((Amount_Per_Pair/2)/df['T1 Close'].iloc[i])
            elif df['Signal'].iloc[i] == 'Long Pair':
                df.loc[df.index[i], 'T1 Position'] = df['T1 Position'].iloc[i-1] if df['T1 Position'].iloc[i-1] > 0 else round((Amount_Per_Pair/2)/df['T1 Close'].iloc[i])
            elif df['Signal'].iloc[i] == 'Flat Pair' and (df['Z-Score'].iloc[i-1]<-LB_exit and df['Z-Score'].iloc[i]>-LB_exit or df['Z-Score'].iloc[i-1]>UB_exit and df['Z-Score'].iloc[i]<UB_exit):
                df.loc[df.index[i], 'T1 Position'] = 0
            else:
                df.loc[df.index[i], 'T1 Position'] = df['T1 Position'].iloc[i-1]
        else:
            df.loc[df.index[i], 'T1 Position'] = 0 if df['Signal'].iloc[i] == 'Flat Pair' else (-round((Amount_Per_Pair/2)/df['T1 Close'].iloc[i]) if df['Signal'].iloc[i] == 'Short Pair' else round((Amount_Per_Pair/2)/df['T1 Close'].iloc[i]))
        
        df.loc[df.index[i], 'T1 Trade'] = df['T1 Position'].iloc[i] - df['T1 Position'].iloc[i-1]

    # Populating the rest of rows for T2 Position
    for i in range(1, len(df)):
        if df['T2 Position'].iloc[i-1] != 0:
            if df['Signal'].iloc[i] == 'Short Pair':
                df.loc[df.index[i], 'T2 Position'] = df['T2 Position'].iloc[i-1] if df['T2 Position'].iloc[i-1] > 0 else round((Amount_Per_Pair/2)/df['T2 Close'].iloc[i])
            elif df['Signal'].iloc[i] == 'Long Pair':
                df.loc[df.index[i], 'T2 Position'] = df['T2 Position'].iloc[i-1] if df['T2 Position'].iloc[i-1] < 0 else -round((Amount_Per_Pair/2)/df['T2 Close'].iloc[i])
            elif df['Signal'].iloc[i] == 'Flat Pair' and (df['Z-Score'].iloc[i-1]<-LB_exit and df['Z-Score'].iloc[i]>-LB_exit or df['Z-Score'].iloc[i-1]>UB_exit and df['Z-Score'].iloc[i]<UB_exit):
                df.loc[df.index[i], 'T2 Position'] = 0
            else:
                df.loc[df.index[i], 'T2 Position'] = df['T2 Position'].iloc[i-1]
        else:
            df.loc[df.index[i], 'T2 Position'] = 0 if df['Signal'].iloc[i] == 'Flat Pair' else (round((Amount_Per_Pair/2)/df['T2 Close'].iloc[i]) if df['Signal'].iloc[i] == 'Short Pair' else -round((Amount_Per_Pair/2)/df['T2 Close'].iloc[i]))
        
        df.loc[df.index[i], 'T2 Trade'] = df['T2 Position'].iloc[i] - df['T2 Position'].iloc[i-1]
    
    # Calculating Transaction Cost
    def Calculate_Transaction_Cost(row):
        multiplier = 1 if row['T1 Trade'] != 0 else 0
        multiplier += 1 if row['T2 Trade'] != 0 else 0
        row['Transaction Cost'] = multiplier * Transaction_Cost
        return row
    
    df = df.apply(Calculate_Transaction_Cost, axis=1)

    # Calculating row 0 T1 Trading Cash, T2 Trading Cash, Total Trading Cash, T1 M2M, T2 M2M, Total M2M, and Pnl
    df.loc[df.index[0], 'T1 Trading Cash'] = -df['T1 Trade'].iloc[0] * df['T1 Close'].iloc[0] 
    df.loc[df.index[0], 'T2 Trading Cash'] = -df['T2 Trade'].iloc[0] * df['T2 Close'].iloc[0] 
    df.loc[df.index[0], 'Total Trading Cash'] = df['T1 Trading Cash'].iloc[0] + df['T2 Trading Cash'].iloc[0] - df['Transaction Cost'].iloc[0]
    df.loc[df.index[0], 'T1 M2M'] = df['T1 Close'].iloc[0] * df['T1 Position'].iloc[0]
    df.loc[df.index[0], 'T2 M2M'] = df['T2 Close'].iloc[0] * df['T2 Position'].iloc[0]
    df.loc[df.index[0], 'Total M2M'] = df['T1 M2M'].iloc[0] + df['T2 M2M'].iloc[0]
    df.loc[df.index[0], 'Pnl'] = df['Total Trading Cash'].iloc[0] + df['Total M2M'].iloc[0]
    
    # Populating the rest of rows for T1 Trading Cash, T2 Trading Cash, Total Trading Cash, T1 M2M, T2 M2M, Total M2M, and Pnl
    for i in range(1, len(df)):
        df.loc[df.index[i], 'T1 Trading Cash'] = df['T1 Trading Cash'].iloc[i-1] - df['T1 Trade'].iloc[i] * df['T1 Close'].iloc[i] 
        df.loc[df.index[i], 'T2 Trading Cash'] = df['T2 Trading Cash'].iloc[i-1] - df['T2 Trade'].iloc[i] * df['T2 Close'].iloc[i] 
        df.loc[df.index[i], 'Total Trading Cash'] = df['T1 Trading Cash'].iloc[i] + df['T2 Trading Cash'].iloc[i] - df['Transaction Cost'].iloc[i]
        df.loc[df.index[i], 'T1 M2M'] = df['T1 Close'].iloc[i] * df['T1 Position'].iloc[i]
        df.loc[df.index[i], 'T2 M2M'] = df['T2 Close'].iloc[i] * df['T2 Position'].iloc[i]
        df.loc[df.index[i], 'Total M2M'] = df['T1 M2M'].iloc[i] + df['T2 M2M'].iloc[i]
        df.loc[df.index[i], 'Pnl'] = df['Total Trading Cash'].iloc[i] + df['Total M2M'].iloc[i]

    return df

# Streamlit app
st.title("Pairs Trading Strategy Backtest")

# Sidebar inputs
st.sidebar.header("Input Parameters")
Ticker1 = st.sidebar.text_input("Ticker 1", "BRX")
Ticker2 = st.sidebar.text_input("Ticker 2", "KIM")
years = st.sidebar.number_input("Years of Data", min_value=1, max_value=20, value=5)
UB_entry = st.sidebar.number_input("Upper Bound Entry Z-Score", value=1)
LB_entry = st.sidebar.number_input("Lower Bound Entry Z-Score", value=1)
UB_exit = st.sidebar.number_input("Upper Bound Exit Z-Score", value=0.5)
LB_exit = st.sidebar.number_input("Lower Bound Exit Z-Score", value=0.5)
Amount_Per_Pair = st.sidebar.number_input("Amount Per Pair", value=10000)
Transaction_Cost = st.sidebar.number_input("Transaction Cost Per Trade", value=0)

# Run the backtest
df = Pairs(Ticker1, Ticker2, years, UB_entry, LB_entry, UB_exit, LB_exit, Amount_Per_Pair, Transaction_Cost)

if df is not None:
    # Show the results table
    st.header("Backtest Results")
    st.write(df)

    # Plot Z-Score over time with entry and exit lines
    st.header("Z-Score and Signal Levels")
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['Z-Score'], label='Z-Score')
    plt.axhline(UB_entry, color='red', linestyle='--', label='Upper Bound Entry')
    plt.axhline(-LB_entry, color='green', linestyle='--', label='Lower Bound Entry')
    plt.axhline(UB_exit, color='red', linestyle=':', label='Upper Bound Exit')
    plt.axhline(-LB_exit, color='green', linestyle=':', label='Lower Bound Exit')
    plt.legend()
    st.pyplot(plt)

    # Plot PnL over time
    st.header("PnL Over Time")
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['Pnl'], label='PnL', color='blue')
    plt.legend()
    st.pyplot(plt)
else:
    st.write("Error: Invalid ticker data. Please check the ticker symbols and try again.")