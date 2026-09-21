import streamlit as st
import re
import tools

st.set_page_config(page_title="Financial Assistant Agent", page_icon="💰", layout="centered")

def agent_process(query):
    query_lower = query.lower()
    
    # 1. EMI Tool
    if "emi" in query_lower:
        numbers = re.findall(r"[\d\.]+", query)
        if len(numbers) >= 3:
            p, r, y = numbers[0], numbers[1], numbers[2]
            return "EMI Calculator", tools.calculate_emi(p, r, y)
        return "EMI Calculator", {"error": "Could not extract principal, rate, and years from the query."}
        
    # 2. Calculator Tool
    elif "calculate " in query_lower and any(op in query_lower for op in ['+', '-', '*', '/']):
        expr_match = re.search(r'calculate\s+([0-9\.\s\+\-\*\/]+)', query_lower)
        if expr_match:
            expr = expr_match.group(1).strip()
            return "Calculator", tools.calculate(expr)
        return "Calculator", {"error": "Could not parse calculation expression."}

    # 3. Stock Price Tool
    elif "price" in query_lower or "stock" in query_lower:
        words = query.replace('?', '').replace('.', '').split()
        symbol = words[-1].upper()
        return "Stock Price", tools.get_stock_price(symbol)
        
    # 4. Financial Information Tool
    elif "financial information" in query_lower or "info" in query_lower:
        words = query.replace('?', '').replace('.', '').split()
        symbol = words[-1].upper()
        return "Financial Information", tools.get_financial_information(symbol)
        
    else:
         return "Unknown", {"error": "I couldn't identify a suitable financial tool for that request."}

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main Title Area
st.title("💰 Financial Assistant Agent")
st.subheader("AI Agent with External Tool Integration")
st.write("This agent analyzes your request, selects the appropriate financial tool, executes it, and returns the result.")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🛠️ Available Tools")
    st.markdown("""
    - 💳 **EMI Calculator**
    - 🧮 **Calculator**
    - 📈 **Stock Price**
    - 🏢 **Financial Information**
    """)
    st.markdown("---")
    st.header("⚙️ How It Works")
    st.markdown("""
    ```text
    User Query
       ↓
    Tool Selection
       ↓
    External Tool
       ↓
    Tool Result
       ↓
    Agent Response
    ```
    """)
    st.info("Market data is provided by Yahoo Finance through yfinance and may be delayed.")
    
    st.markdown("---")
    st.header("⚡ Quick Actions")
    if st.button("💳 Calculate EMI"):
        st.session_state.prompt_override = "Calculate EMI for 500000 at 8.5% for 5 years."
    if st.button("🧮 Calculator"):
        st.session_state.prompt_override = "Calculate 25 * 48."
    if st.button("📈 Stock Price"):
        st.session_state.prompt_override = "What is the current price of RELIANCE?"
    if st.button("🏢 Company Info"):
        st.session_state.prompt_override = "Give me financial information about TCS."

# Check for quick action override
prompt = st.chat_input("Enter a financial or calculation request...")
if "prompt_override" in st.session_state:
    prompt = st.session_state.prompt_override
    del st.session_state.prompt_override

# Render existing chat
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.write(msg["content"])

if prompt:
    # 1. User Message
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Agent Processing
    tool_name, tool_data = agent_process(prompt)
    
    # 3. Assistant Message
    with st.chat_message("assistant"):
        if tool_name != "Unknown":
            st.info(f"**🔧 Tool Selected**\n\n{tool_name}")
            
        if tool_data.get("error"):
            # If API fails or unknown tool
            error_msg = tool_data["error"]
            if "unavailable" in error_msg.lower() or "reach" in error_msg.lower():
                st.warning("⚠️ The external financial-data service could not be reached right now.")
                st.session_state.messages.append({"role": "assistant", "content": "⚠️ The external financial-data service could not be reached right now."})
            else:
                st.warning(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        else:
            # Render Tool Output Formatted
            if tool_name == "EMI Calculator":
                st.markdown(f"### Monthly EMI\n**{tool_data['emi']}**")
                st.caption(f"**Loan Amount:** Rs. {tool_data['principal']:,.0f} | **Interest Rate:** {tool_data['rate']}% | **Duration:** {tool_data['years']} years")
                
            elif tool_name == "Calculator":
                st.markdown(f"### Result\n**{tool_data['result']}**")
                
            elif tool_name == "Stock Price":
                st.markdown(f"### 📈 {tool_data['symbol']}")
                st.metric("Current / Last Price", tool_data['price'])
                st.caption("Market data is provided by Yahoo Finance through yfinance and may be delayed.")
                
            elif tool_name == "Financial Information":
                st.markdown(f"### 🏢 {tool_data['name']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Symbol:** {tool_data['symbol']}")
                    st.write(f"**Exchange:** {tool_data['exchange']}")
                    st.write(f"**Sector:** {tool_data['sector']}")
                with col2:
                    st.write(f"**Industry:** {tool_data['industry']}")
                    st.write(f"**Current Price:** {tool_data['current_price']}")
                    st.write(f"**Market Cap:** {tool_data['market_cap']}")
                    
            # Save raw representation to history so it persists across reruns (Streamlit native Markdown)
            # We don't save the UI components themselves to session state, just a string representation
            # Actually, to make history look identical, we can save the markdown.
            # But the requirement doesn't strictly need history to be styled the exact same way, just "Display previous conversation messages."
            # For simplicity, we just save a summary of what the agent said to the chat.
            if tool_name == "EMI Calculator":
                summary = f"**🔧 Tool Selected:** {tool_name}\n\n**Monthly EMI:** {tool_data['emi']}\n*(Principal: {tool_data['principal']}, Rate: {tool_data['rate']}%, Years: {tool_data['years']})*"
            elif tool_name == "Calculator":
                summary = f"**🔧 Tool Selected:** {tool_name}\n\n**Result:** {tool_data['result']}"
            elif tool_name == "Stock Price":
                summary = f"**🔧 Tool Selected:** {tool_name}\n\n**{tool_data['symbol']} Current Price:** {tool_data['price']}"
            elif tool_name == "Financial Information":
                summary = f"**🔧 Tool Selected:** {tool_name}\n\n**Company:** {tool_data['name']}\n**Sector:** {tool_data['sector']}\n**Market Cap:** {tool_data['market_cap']}"
            
            st.session_state.messages.append({"role": "assistant", "content": summary})
