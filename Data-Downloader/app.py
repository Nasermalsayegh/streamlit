import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Helper function to calculate date ranges
def get_date_range(option):
    today = datetime.today()
    if option == "1 Year":
        return today - timedelta(days=365), today
    elif option == "3 Years":
        return today - timedelta(days=365 * 3), today
    elif option == "5 Years":
        return today - timedelta(days=365 * 5), today
    elif option == "All":
        return today - timedelta(days=365 * 1000), today
    return None, None

# Sidebar for inputs
st.sidebar.title("Stock Data Input")
tickers = st.sidebar.text_input("Enter ticker symbols (e.g., AAPL MSFT)", "AAPL")
interval = st.sidebar.selectbox("Select interval", ['1d', '1wk', '1mo', '3mo'])

# Predefined date ranges
date_option = st.sidebar.selectbox("Select Date Range", ["1 Year", "3 Years", "5 Years", "All", "Custom"])
start_date, end_date = get_date_range(date_option)

# If "Custom" is selected, let the user pick exact start and end dates
if date_option == "Custom":
    start_date = st.sidebar.date_input("Start date", datetime(2020, 1, 1))
    end_date = st.sidebar.date_input("End date", datetime(2023, 1, 1))

# Tab structure for different features
tab1, tab2 = st.tabs(["Stock Data", "Company Financials"])

# First tab: Stock Data Download
with tab1:
    st.title(" Historical Stock Data")

    # Automatically download stock data based on user input
    df = yf.download(tickers, start=start_date, end=end_date, interval=interval)
    
    if not df.empty:
        st.write(f"Stock Data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}:")
        st.dataframe(df)
        csv = df.to_csv().encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f'{tickers.replace(" ", "_")}_stock_data.csv',
            mime='text/csv',
        )
    else:
        st.error("No data found for the selected parameters.")

# Second tab: Company Financials Download
with tab2:
    st.title("Download Company Financials")

    # User input for financials
    financial_ticker = st.text_input("Enter company ticker for financials (e.g., AAPL, MSFT)", "AAPL")
    
    # Automatically download company financials
    ticker_obj = yf.Ticker(financial_ticker)
    
    # Balance Sheet
    balance_sheet = ticker_obj.balance_sheet
    if not balance_sheet.empty:
        st.subheader("Balance Sheet")
        st.dataframe(balance_sheet)
        balance_csv = balance_sheet.to_csv().encode('utf-8')
        st.download_button(
            label="Download Balance Sheet CSV",
            data=balance_csv,
            file_name=f'{financial_ticker}_balance_sheet.csv',
            mime='text/csv',
        )
    else:
        st.error("Balance sheet not available.")
    
    # Income Statement
    income_statement = ticker_obj.financials
    if not income_statement.empty:
        st.subheader("Income Statement")
        st.dataframe(income_statement)
        income_csv = income_statement.to_csv().encode('utf-8')
        st.download_button(
            label="Download Income Statement CSV",
            data=income_csv,
            file_name=f'{financial_ticker}_income_statement.csv',
            mime='text/csv',
        )
    else:
        st.error("Income statement not available.")
