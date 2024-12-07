import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import datetime
import re

# Helper Function to Clean Column Names
def clean_column_names(columns):
    return [col.strip().lower() for col in columns]

# Helper Function to Detect Data Type
def detect_data_type(data):
    columns = clean_column_names(data.columns)
    
    # Sales Data Type Check
    if {'date', 'product name', 'units sold', 'revenue'}.issubset(columns):
        return "Sales"
    # Financial Data Type Check
    elif {'date', 'expense type', 'amount', 'income', 'net profit/loss'}.issubset(columns):
        return "Financial"
    # Inventory Data Type Check
    elif {'item name', 'current stock', 'restock date', 'sales rate'}.issubset(columns):
        return "Inventory"
    # Employee Performance Data Type Check
    elif {'employee name', 'tasks completed', 'hours worked', 'ratings'}.issubset(columns):
        return "Employee Performance"
    # Marketing Data Type Check
    elif {'campaign name', 'reach', 'clicks', 'conversions', 'revenue generated'}.issubset(columns):
        return "Marketing"
    # Customer Feedback Data Type Check
    elif {'customer name', 'feedback rating', 'product/service', 'date'}.issubset(columns):
        return "Customer Feedback"
    # Education Data Type Check
    elif {'student name', 'subject', 'marks', 'attendance'}.issubset(columns):
        return "Education"
    # Project Management Data Type Check
    elif {'task name', 'start date', 'end date', 'assigned to', 'status'}.issubset(columns):
        return "Project Management"
    else:
        return "Unknown"

# Analysis Functions for Each Type
def sales_analysis(data):
    st.subheader("Sales Analysis")
    # Top-selling products
    top_products = data.groupby('product name')['units sold'].sum().sort_values(ascending=False)
    st.write("Top-Selling Products:")
    st.bar_chart(top_products)
    # Revenue Trend
    st.line_chart(data.groupby('date')['revenue'].sum())

def financial_analysis(data):
    st.subheader("Financial Analysis")
    # Expense Analysis
    expense_analysis = data.groupby('expense type')['amount'].sum().sort_values(ascending=False)
    st.write("Expense Distribution:")
    st.pie_chart(expense_analysis)
    # Profit/Loss Trend
    st.line_chart(data.groupby('date')['net profit/loss'].sum())

def inventory_analysis(data):
    st.subheader("Inventory Analysis")
    # Ensure columns are clean
    data.columns = clean_column_names(data.columns)
    
    # Stock Levels - Adjust to match cleaned column names
    if 'item name' in data.columns and 'current stock' in data.columns:
        st.write("Current Stock Levels:")
        st.bar_chart(data.set_index('item name')['current stock'])
    
    # Restock Prediction - Adjust to match cleaned column names
    if 'restock date' in data.columns and 'sales rate' in data.columns:
        st.line_chart(data.set_index('restock date')['sales rate'])

# Dynamic Analysis
def dynamic_analysis(data_type, data):
    if data_type == "Sales":
        sales_analysis(data)
    elif data_type == "Financial":
        financial_analysis(data)
    elif data_type == "Inventory":
        inventory_analysis(data)
    else:
        st.warning("Data type not recognized for detailed analysis. Showing raw data.")
        st.write(data)

# Function to extract data from a paragraph
def extract_data_from_paragraph(paragraph):
    # Regular expression to match key patterns
    date_pattern = r'\b(?:\w+\s\d{1,2},\s\d{4})\b'
    product_pattern = r'\b(?:laptops|item|product)\b'
    units_sold_pattern = r'\b(\d+)\s+laptops'
    revenue_pattern = r'\b\$\d{1,3}(?:,\d{3})*\b'
    expenses_pattern = r'\bExpenses for both days were \$(\d{1,3}(?:,\d{3})*)\b'
    profit_pattern = r'profits of \$(\d{1,3}(?:,\d{3})*)\b'
    
    # Find all matches for each pattern
    dates = re.findall(date_pattern, paragraph)
    units_sold = [int(unit) for unit in re.findall(units_sold_pattern, paragraph)]
    revenues = [float(revenue.replace('$', '').replace(',', '')) for revenue in re.findall(revenue_pattern, paragraph)]
    expenses = [float(expense.replace('$', '').replace(',', '')) for expense in re.findall(expenses_pattern, paragraph)]
    profits = [float(profit.replace('$', '').replace(',', '')) for profit in re.findall(profit_pattern, paragraph)]

    # If no dates are found, assign the current date
    if not dates:
        dates = [datetime.datetime.now().strftime("%B %d, %Y")]
    
    # Ensure all lists have the same length by padding with None or another placeholder
    max_length = max(len(dates), len(units_sold), len(revenues), len(expenses), len(profits))
    
    dates.extend([dates[-1]] * (max_length - len(dates)))
    units_sold.extend([None] * (max_length - len(units_sold)))
    revenues.extend([None] * (max_length - len(revenues)))
    expenses.extend([None] * (max_length - len(expenses)))
    profits.extend([None] * (max_length - len(profits)))
    
    # If revenue is missing but units sold is available, calculate it (for example, unit price of 500)
    for i in range(len(revenues)):
        if revenues[i] is None and units_sold[i] is not None:
            revenues[i] = units_sold[i] * 500  # Assuming unit price of 500 (adjust as needed)

    # If expenses are missing, calculate them (you can apply your own logic here, e.g., 20% of revenue)
    for i in range(len(expenses)):
        if expenses[i] is None:
            if revenues[i] is not None:
                expenses[i] = revenues[i] * 0.2  # Assuming expenses are 20% of revenue (adjust as needed)

    # Create DataFrame
    data = pd.DataFrame({
        'date': pd.to_datetime(dates),
        'units sold': units_sold,
        'revenue': revenues,
        'expenses': expenses,
        'profit': profits
    })
    
    return data

# Streamlit App Layout
st.set_page_config(page_title="Intelligent Data Analysis App", layout="wide")
st.title("Intelligent Data Analysis and Projection App")

# Choose between uploading a file or entering a paragraph
option = st.selectbox("Choose input type", ["Upload Excel File", "Enter Sales Data Paragraph"])

if option == "Upload Excel File":
    uploaded_file = st.file_uploader("Upload your file (Excel)", type=["xlsx"])
    if uploaded_file:
        # Load Data
        df = pd.read_excel(uploaded_file)
        st.subheader("Uploaded Data")
        st.write(df)
        
        # Detect Data Type
        detected_type = detect_data_type(df)
        st.info(f"Detected Data Type: {detected_type}")
        
        # Perform Dynamic Analysis
        dynamic_analysis(detected_type, df)
        
        # Future Projections
        st.subheader("Future Projections")
        period = st.selectbox("Select projection period", ["Days", "Weeks", "Months", "Years"])
        projection_factor = st.slider(f"Select number of {period.lower()} for projection", 1, 100, 10)
        
        # Generate projections based on date column or create a date column
        date_col = next((col for col in df.columns if 'date' in col.lower()), None)
        if date_col:
            future_dates = [pd.to_datetime(max(df[date_col])) + pd.Timedelta(days=i * (7 if period == "Weeks" else 30 if period == "Months" else 365 if period == "Years" else 1)) for i in range(projection_factor)]
            projection_df = pd.DataFrame({"date": future_dates, "projected value": [i * 1.1 for i in range(len(future_dates))]})
            st.write(projection_df)
            st.line_chart(projection_df.set_index('date'))
        else:
            # Create a synthetic date column for projections
            start_date = datetime.datetime.now()
            future_dates = [start_date + datetime.timedelta(days=i * (7 if period == "Weeks" else 30 if period == "Months" else 365 if period == "Years" else 1)) for i in range(projection_factor)]
            projection_df = pd.DataFrame({"date": future_dates, "projected value": [i * 1.1 for i in range(len(future_dates))]})
            st.write("No date column found. Using synthetic dates for projections:")
            st.write(projection_df)
            st.line_chart(projection_df.set_index('date'))

elif option == "Enter Sales Data Paragraph":
    # Input box for the user to enter the paragraph
    paragraph = st.text_area("Enter paragraph with sales data:")
    if paragraph:
        # Extract data from the entered paragraph
        extracted_data = extract_data_from_paragraph(paragraph)
        
        # Display extracted data
        st.subheader("Extracted Data:")
        st.write(extracted_data)
        
        # Plotting graphs based on the extracted data
        st.subheader("Revenue and Profit Trend")
        st.line_chart(extracted_data[['revenue', 'profit']])
        st.subheader("Units Sold")
        st.bar_chart(extracted_data['units sold'])
        st.subheader("Expenses Breakdown")
        st.bar_chart(extracted_data['expenses'])
