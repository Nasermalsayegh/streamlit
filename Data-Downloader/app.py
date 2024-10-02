import streamlit as st
import yfinance as yf

# Tab structure for different features
tab1, tab2, tab3 = st.tabs(["Stock Data", "Company Financials", "Valuation"])

# First tab: Stock Data Download
with tab1:
    st.title("Historical Stock Data")

    # Inputs for Stock Data
    tickers = st.text_input("Enter ticker symbols (e.g., AAPL MSFT)", "AAPL")
    interval = st.selectbox("Select interval", ['1d', '1wk', '1mo', '3mo'])
    date_option = st.selectbox("Select Date Range", ["1 Year", "3 Years", "5 Years", "All", "Custom"])
    
    # Automatically download stock data based on user input
    df = yf.download(tickers, period="5y", interval=interval)
    
    if not df.empty:
        st.write("Stock Data:")
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

    financial_ticker = st.text_input("Enter company ticker for financials (e.g., AAPL, MSFT)", "AAPL", key="financials")
    
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

# Third tab: Stock Valuation using Benjamin Graham Valuation Equation
with tab3:
    st.title("Stock Valuation")

    # Inputs for Benjamin Graham Valuation
    earnings_per_share = st.number_input("Enter Earnings per Share (EPS)", value=5.0)
    growth_rate_eps = st.number_input("Enter estimated growth rate for EPS (as a percentage)", 0.0, 100.0, 5.0)
    discount_rate = st.number_input("Enter discount rate (as a percentage)", 0.0, 100.0, 10.0)

    # Benjamin Graham Valuation Equation Calculation
    graham_stock_price = (earnings_per_share * (8.5 + 2 * growth_rate_eps)) * 4.4 / discount_rate

    # Display the result in a larger font with light blue background, rounded edges
    st.write(f"""
        <div style='text-align: center; background-color: #d9edf7; padding: 15px; 
                    border-radius: 10px; font-size: 24px; color: #31708f;'>
            Estimated stock price using Benjamin Graham Valuation: <strong>${graham_stock_price:.2f}</strong>
        </div>
    """, unsafe_allow_html=True)

    # LaTeX for Benjamin Graham Valuation Equation
    st.latex(r'''
    \text{Benjamin Graham Valuation Equation:} \ P = \frac{E \times (8.5 + 2 \times g_{\text{EPS}}) \times 4.4}{r}
    ''')

    # Bullet points explaining the variables in the formula
    st.markdown("""
    **Where:**
    - **P** = Price
    - **E** = Earnings per Share (EPS)
    - **g** = Growth Rate of EPS
    - **r** = Discount Rate
    """)
