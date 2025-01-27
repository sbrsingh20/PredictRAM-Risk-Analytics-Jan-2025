import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Read data from the original Excel file
file_path = "merged_stock_data_with_categories_in_cells_nov2024.xlsx"
df = pd.read_excel(file_path)

# Read data from the additional Excel file with calculated metrics
metrics_file_path = "calculated_stock_metrics_full.xlsx"
metrics_df = pd.read_excel(metrics_file_path)

# Categories and risk thresholds from the original code
risk_categories = {
    "Market Risk": {
        "Volatility": (0.1, 0.2),
        "Beta": (0.5, 1.5),
        "Correlation with ^NSEI": (0.7, 1),
    },
    "Financial Risk": {
        "debtToEquity": (0.5, 1.5),
        "currentRatio": (1.5, 2),
        "quickRatio": (1, 1.5),
        "Profit Margins": (20, 30),
        "returnOnAssets": (10, 20),
        "returnOnEquity": (15, 25),
    },
    "Liquidity Risk": {
        "Volume": (1_000_000, float('inf')),
        "Average Volume": (500_000, 1_000_000),
        "marketCap": (10_000_000_000, float('inf')),
    },
}

def categorize_risk(value, thresholds):
    """Categorizes risk based on predefined thresholds."""
    try:
        value = float(value)
    except (ValueError, TypeError):
        return "Data not available"

    if value < thresholds[0]:
        return "Good"
    elif thresholds[0] <= value <= thresholds[1]:
        return "Neutral"
    else:
        return "Bad"

def get_risk_color(risk_level):
    """Returns the color associated with a risk level."""
    if risk_level == "Good":
        return "green"
    elif risk_level == "Neutral":
        return "yellow"
    elif risk_level == "Bad":
        return "red"
    else:
        return "black"

def calculate_risk_parameters(stock_symbols):
    """Calculates and categorizes risk parameters for a given stock portfolio."""
    results = []
    stock_scores = {}
    category_scores = {category: 0 for category in risk_categories}
    total_portfolio_score = 0

    # Iterate over each stock symbol
    for stock_symbol in stock_symbols:
        # Get data from Excel file
        stock_info = df[df['Stock Symbol'] == stock_symbol]

        if stock_info.empty:
            print(f"No data found for stock symbol: {stock_symbol}")
            continue

        stock_info = stock_info.iloc[0]  # Get the first row for the stock

        # Initialize summary for the stock
        total_stock_score = 0
        summary = {category: {'Good': 0, 'Neutral': 0, 'Bad': 0, 'Data not available': 0} for category in risk_categories}

        # Process each risk category and its parameters
        for category, parameters in risk_categories.items():
            for param, thresholds in parameters.items():
                value = stock_info.get(param)

                if value is not None:
                    risk_level = categorize_risk(value, thresholds)
                    summary[category][risk_level] += 1
                    results.append({
                        'Stock Symbol': stock_symbol,
                        'Category': category,
                        'Parameter': param,
                        'Value': value,
                        'Risk Level': risk_level,
                        'Color': get_risk_color(risk_level)
                    })

                    if risk_level == "Good":
                        category_scores[category] += 1
                        total_portfolio_score += 1
                        total_stock_score += 1
                    elif risk_level == "Bad":
                        category_scores[category] -= 1
                        total_portfolio_score -= 1
                        total_stock_score -= 1
                else:
                    results.append({
                        'Stock Symbol': stock_symbol,
                        'Category': category,
                        'Parameter': param,
                        'Value': 'Data not available',
                        'Risk Level': 'Data not available',
                        'Color': 'black'
                    })
                    summary[category]['Data not available'] += 1

        stock_scores[stock_symbol] = total_stock_score  # Save the score for the stock

    return results, category_scores, stock_scores, total_portfolio_score

# Streamlit UI components
st.title("Stock Risk Analysis Dashboard")

# Dropdown to select stocks
selected_stocks = st.multiselect(
    "Select stocks",
    options=df['Stock Symbol'].unique(),
    default=df['Stock Symbol'].unique()[0]
)

# Calculate risk parameters for the selected stocks
results, category_scores, stock_scores, total_portfolio_score = calculate_risk_parameters(selected_stocks)

# Display the summary
st.subheader("Summary")
summary_text = f"Total Portfolio Score: {total_portfolio_score}\n"
for category, score in category_scores.items():
    summary_text += f"{category}: {score}\n"
st.text(summary_text)

# Display risk category tables
st.subheader("Market Risk")
market_risk_data = [result for result in results if result['Category'] == "Market Risk"]
st.dataframe(pd.DataFrame(market_risk_data))

st.subheader("Financial Risk")
financial_risk_data = [result for result in results if result['Category'] == "Financial Risk"]
st.dataframe(pd.DataFrame(financial_risk_data))

st.subheader("Liquidity Risk")
liquidity_risk_data = [result for result in results if result['Category'] == "Liquidity Risk"]
st.dataframe(pd.DataFrame(liquidity_risk_data))

# Display best stock based on Investment Score
if stock_scores:
    best_stock = max(stock_scores, key=stock_scores.get)
    best_stock_data = {
        "Stock Symbol": best_stock,
        "Investment Score": stock_scores[best_stock]
    }
    st.subheader("Best Stock")
    st.write(best_stock_data)

# Display additional stock metrics
st.subheader("Additional Stock Metrics")
metrics_data = metrics_df[metrics_df['Stock Symbol'].isin(selected_stocks)][[ 
    'Stock Symbol', 'Correlation (Minute)', 'Annualized Alpha (%)', 'Annualized Volatility (%)',
    'Sharpe Ratio (Daily)', 'Treynor Ratio (Daily)', 'Sortino Ratio (Daily)', 'Maximum Drawdown (Daily)', 
    'R-Squared (Daily)', 'Downside Deviation (Daily)', 'Tracking Error (%)', 'VaR (95%)', 
    'Annualized Alpha (Monthly)', 'Annualized Volatility (Monthly)', 'Sharpe Ratio (Monthly)', 
    'Treynor Ratio (Monthly)', 'Sortino Ratio (Monthly)', 'Maximum Drawdown (Monthly)', 
    'R-Squared (Monthly)', 'Downside Deviation (Monthly)', 'Tracking Error (%) (Monthly)', 
    'VaR (95%) (Monthly)', 'Annualized Alpha (Annual)', 'Annualized Volatility (Annual)', 
    'Sharpe Ratio (Annual)', 'Treynor Ratio (Annual)', 'Sortino Ratio (Annual)', 
    'Annualized Alpha (Minute)', 'Annualized Volatility (Minute)', 'Sharpe Ratio (Minute)', 
    'Treynor Ratio (Minute)', 'Sortino Ratio (Minute)', 'Maximum Drawdown (Minute)', 
    'R-Squared (Minute)', 'Downside Deviation (Minute)', 'Tracking Error (%) (Minute)', 'VaR (95%) (Minute)'
]].to_dict('records')
st.dataframe(metrics_data)

# Display risk graphs for each parameter (Market Risk, Financial Risk, Liquidity Risk)
def plot_risk_graphs(results, category):
    # Filter results by category
    filtered_results = [r for r in results if r['Category'] == category]
    param_counts = {}

    for result in filtered_results:
        param = result['Parameter']
        risk_level = result['Risk Level']
        if param not in param_counts:
            param_counts[param] = {"Good": 0, "Neutral": 0, "Bad": 0, "Data not available": 0}
        param_counts[param][risk_level] += 1

    # Create a bar chart for each parameter
    for param, counts in param_counts.items():
        fig = go.Figure()
        fig.add_trace(go.Bar(x=list(counts.keys()), y=list(counts.values()), name=param))
        fig.update_layout(title=f"Risk Distribution for {param} in {category}", xaxis_title="Risk Level", yaxis_title="Count")
        st.plotly_chart(fig)

# Display risk parameter graphs for each category
st.subheader("Risk Distribution by Parameter")
for category in risk_categories.keys():
    plot_risk_graphs(results, category)

# Display investment score bar chart
investment_data = [{"Stock Symbol": stock, "Investment Score": score} for stock, score in stock_scores.items()]
investment_df = pd.DataFrame(investment_data)
fig = px.bar(investment_df, x="Stock Symbol", y="Investment Score", title="Investment Scores for Selected Stocks")
st.plotly_chart(fig)

# Display total portfolio score
st.subheader("Total Portfolio Score")
st.write({
    "Portfolio Score": total_portfolio_score
})
