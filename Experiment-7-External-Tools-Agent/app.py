import streamlit as st
import re
import tools

def agent_process(query):
    query_lower = query.lower()
    
    # 1. EMI Tool
    if "emi" in query_lower:
        # Extract Principal, Rate, Years using regex
        # Example: Calculate EMI for a loan of 500000 at 8.5% for 5 years.
        numbers = re.findall(r"[\d\.]+", query)
        if len(numbers) >= 3:
            p, r, y = numbers[0], numbers[1], numbers[2]
            result = tools.calculate_emi(p, r, y)
            return "EMI Calculator", f"Monthly EMI: {result}"
        return "EMI Calculator", "Error: Could not extract principal, rate, and years from the query. Please ensure you provide all three numbers."
        
    # 2. Calculator Tool
    # Check for math operators: +, -, *, /
    elif "calculate " in query_lower and any(op in query_lower for op in ['+', '-', '*', '/']):
        # Extract expression
        expr_match = re.search(r'calculate\s+([0-9\.\s\+\-\*\/]+)', query_lower)
        if expr_match:
            expr = expr_match.group(1).strip()
            result = tools.calculate(expr)
            return "General Calculator", f"Result: {result}"
        return "General Calculator", "Error: Could not parse calculation expression. Use format 'Calculate A + B'."

    # 3. Stock Price Tool
    elif "price" in query_lower or "stock" in query_lower:
        # Extract symbol (assumes uppercase word or last word)
        # E.g., What is the current price of RELIANCE?
        words = query.replace('?', '').replace('.', '').split()
        symbol = words[-1].upper()
        result = tools.get_stock_price(symbol)
        return "Stock Price Tool", result
        
    # 4. Financial Information Tool
    elif "financial information" in query_lower or "info" in query_lower:
        # Extract symbol
        words = query.replace('?', '').replace('.', '').split()
        symbol = words[-1].upper()
        result = tools.get_financial_information(symbol)
        return "Financial Information Tool", result
        
    else:
         return "Unknown", "I couldn't understand the request. Please ask about EMI, general calculations, stock prices, or financial information."

st.set_page_config(page_title="Financial Assistant Agent", page_icon="💰")
st.title("Financial Assistant Agent 💰")
st.write("An intelligent agent that uses external tools to calculate EMIs, perform math, and fetch stock data.")

# Add notice about API
st.info("Note: Stock market data is fetched using Yahoo Finance (yfinance) and may be delayed.")

# Chat input
if query := st.chat_input("Enter a financial or calculation request..."):
    # Display user query
    st.chat_message("user").write(query)
    
    # Process through agent
    tool_name, result = agent_process(query)
    
    # Display assistant response and tool used
    with st.chat_message("assistant"):
        st.markdown(f"**Selected Tool:**\n{tool_name}")
        st.markdown(f"**Tool Result:**\n{result}")
