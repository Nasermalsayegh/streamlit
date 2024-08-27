import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import norm
import plotly.graph_objects as go

# -------------------------------
# Streamlit Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Option Pricing Dashboard",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------
# Custom CSS Styles
# -------------------------------
st.markdown("""
<style>
/* General Styles */
body {
    background-color: #f5f5f5;
    color: #333333;
}
 
/* Header Styles */
.header-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #2E4053;
    text-align: center;
    margin-bottom: 20px;
}

/* Metric Styles */
.metric-box {
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    color: white;
}

.metric-call {
    background-color: #3498db; /* Blue for Call */
}

.metric-put {
    background-color: #e67e22; /* Orange for Put */
}

/* Footer Styles */
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #2E4053;
    color: white;
    text-align: center;
    padding: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Option Pricing Calculator Class
# -------------------------------
class OptionPricingCalculator:
    """
    A class to calculate European Call and Put option prices using the Black-Scholes model.
    """

    def __init__(self, S, K, T, r, sigma):
        """
        Initializes the calculator with market parameters.
        
        Parameters:
        - S: Current stock price
        - K: Strike price
        - T: Time to maturity (in years)
        - r: Risk-free interest rate
        - sigma: Volatility of the underlying asset
        """
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self._calculate_d1_d2()

    def _calculate_d1_d2(self):
        """
        Calculates the d1 and d2 parameters used in Black-Scholes formulas.
        """
        self.d1 = (np.log(self.S / self.K) + (self.r + 0.5 * self.sigma ** 2) * self.T) / \
                  (self.sigma * np.sqrt(self.T))
        self.d2 = self.d1 - self.sigma * np.sqrt(self.T)

    def calculate_call_price(self):
        """
        Calculates the European Call option price.
        """
        call_price = self.S * norm.cdf(self.d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(self.d2)
        return call_price

    def calculate_put_price(self):
        """
        Calculates the European Put option price.
        """
        put_price = self.K * np.exp(-self.r * self.T) * norm.cdf(-self.d2) - self.S * norm.cdf(-self.d1)
        return put_price

    def calculate_greeks(self):
        """
        Calculates the Delta and Gamma Greeks for both Call and Put options.
        """
        delta_call = norm.cdf(self.d1)
        delta_put = delta_call - 1
        gamma = norm.pdf(self.d1) / (self.S * self.sigma * np.sqrt(self.T))
        return {
            'Delta Call': delta_call,
            'Delta Put': delta_put,
            'Gamma': gamma
        }

# -------------------------------
# Sidebar Inputs
# -------------------------------
st.sidebar.title("💡 Input Parameters")

with st.sidebar.form(key='parameters_form'):
    current_price = st.number_input("Current Stock Price (S)", value=100.0, min_value=0.01, step=0.1)
    strike_price = st.number_input("Strike Price (K)", value=100.0, min_value=0.01, step=0.1)
    time_to_maturity = st.number_input("Time to Maturity (T in years)", value=1.0, min_value=0.01, step=0.01)
    risk_free_rate = st.number_input("Risk-Free Interest Rate (r)", value=0.05, min_value=0.0, step=0.01, format="%.4f")
    volatility = st.number_input("Volatility (σ)", value=0.2, min_value=0.01, step=0.01, format="%.4f")

    submit_button = st.form_submit_button(label='Calculate')

st.sidebar.markdown("""
[Connect with me on LinkedIn](https://www.linkedin.com/in/nasermalsayegh/)
""")

# -------------------------------
# Main Page Content
# -------------------------------
st.markdown("<h1 class='header-title'>European Option Pricing Dashboard</h1>", unsafe_allow_html=True)

if submit_button:
    # Initialize the calculator
    opc = OptionPricingCalculator(
        S=current_price,
        K=strike_price,
        T=time_to_maturity,
        r=risk_free_rate,
        sigma=volatility
    )

    # Calculate Prices and Greeks
    call_price = opc.calculate_call_price()
    put_price = opc.calculate_put_price()
    greeks = opc.calculate_greeks()

    # Display Results
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box metric-call">
            <h3>Call Option Price</h3>
            <p>${call_price:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box metric-put">
            <h3>Put Option Price</h3>
            <p>${put_price:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display Greeks
    st.subheader("Option Greeks")
    greeks_df = pd.DataFrame(greeks, index=[0])
    st.table(greeks_df.style.format("{:.4f}"))
    
    st.markdown("---")
    
    # Additional Plot: Delta Surface
    st.subheader("Delta Surface Plot")
    
    # Create grids for S and sigma
    S_range = np.linspace(80.0, 120.0, 25)
    sigma_range = np.linspace(0.2, 0.8, 25)
    S_grid, sigma_grid = np.meshgrid(S_range, sigma_range)
    
    # Calculate Delta over the grid
    delta_calls = np.vectorize(lambda S, sigma: OptionPricingCalculator(S, strike_price, time_to_maturity, risk_free_rate, sigma).calculate_greeks()['Delta Call'])(S_grid, sigma_grid)
    
    fig_delta = go.Figure(data=[go.Surface(z=delta_calls, x=S_range, y=sigma_range)])
    fig_delta.update_layout(
        title='Call Option Delta Surface',
        scene=dict(
            xaxis_title='Stock Price (S)',
            yaxis_title='Volatility (σ)',
            zaxis_title='Delta',
        ),
        autosize=True,
        margin=dict(l=65, r=50, b=65, t=90)
    )
    
    st.plotly_chart(fig_delta, use_container_width=True)

# -------------------------------
# Footer
# -------------------------------
st.markdown("""
<div class="footer">
    <p>Developed by <a href="https://www.linkedin.com/in/nasermalsayegh/" style="color: #ecf0f1; text-decoration: none;">Naser Alsayegh</a> | © 2024 All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
