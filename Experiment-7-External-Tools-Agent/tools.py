import re
import operator
import yfinance as yf

def calculate_emi(principal, annual_rate, duration_years):
    try:
        p = float(principal)
        r = float(annual_rate) / 12 / 100
        n = float(duration_years) * 12
        
        if r == 0:
            emi = p / n if n > 0 else 0
            return f"Rs. {round(emi, 2):,}"
            
        emi = p * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
        return f"Rs. {round(emi, 2):,}"
    except Exception as e:
        return f"Error calculating EMI: {str(e)}"

def calculate(expression):
    try:
        # Very basic safe calculator for +, -, *, /
        # Find numbers and operator
        match = re.match(r'^\s*([0-9.]+)\s*([\+\-\*\/])\s*([0-9.]+)\s*$', expression)
        if not match:
            return "Error: Invalid expression. Only basic arithmetic with two numbers is supported (e.g., 25 * 48)."
        
        num1, op, num2 = float(match.group(1)), match.group(2), float(match.group(3))
        
        ops = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv
        }
        
        if op == '/' and num2 == 0:
            return "Error: Division by zero."
            
        result = ops[op](num1, num2)
        
        # Format result to drop trailing .0
        if result.is_integer():
            return str(int(result))
        return str(round(result, 4))
    except Exception as e:
        return f"Error: {str(e)}"

def get_stock_price(symbol):
    try:
        # Heuristic for Indian stocks as requested in examples
        indian_stocks = ['RELIANCE', 'TCS', 'INFY']
        if symbol.upper() in indian_stocks:
            symbol = symbol.upper() + '.NS'
            
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="1d")
        
        if history.empty:
            # Try appending .NS if not empty to see if it's an Indian stock not in list
            if not symbol.endswith('.NS'):
                ticker = yf.Ticker(symbol + ".NS")
                history = ticker.history(period="1d")
                if history.empty:
                    return f"Error: Could not retrieve price for {symbol}. It might be invalid or delisted."
                symbol = symbol + ".NS"
            else:
                return f"Error: Could not retrieve price for {symbol}."
        
        last_price = history['Close'].iloc[-1]
        currency = "Rs. " if symbol.endswith(".NS") or symbol.endswith(".BO") else "$"
        return f"The current/last closing price of {symbol} is {currency}{last_price:.2f}"
    except Exception as e:
        return f"Error retrieving stock price: API might be unavailable. Detail: {str(e)}"

def get_financial_information(symbol):
    try:
        indian_stocks = ['RELIANCE', 'TCS', 'INFY']
        if symbol.upper() in indian_stocks:
            symbol = symbol.upper() + '.NS'
            
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if 'shortName' not in info and 'longName' not in info:
             # Retry with .NS if not found
             if not symbol.endswith('.NS'):
                ticker = yf.Ticker(symbol + ".NS")
                info = ticker.info
                if 'shortName' not in info and 'longName' not in info:
                    return f"Error: Could not retrieve information for {symbol}."
                symbol = symbol + ".NS"
             else:
                 return f"Error: Could not retrieve info for {symbol}."
             
        name = info.get('shortName', info.get('longName', 'Unknown'))
        industry = info.get('industry', 'Unknown')
        market_cap = info.get('marketCap', 'Unknown')
        
        # Format market cap
        if isinstance(market_cap, (int, float)):
             market_cap = f"{market_cap:,}"
             
        summary = info.get('longBusinessSummary', 'No summary available.')
        if len(summary) > 250:
            summary = summary[:247] + "..."
        
        return f"**Company**: {name}\n\n**Industry**: {industry}\n\n**Market Cap**: {market_cap}\n\n**Summary**: {summary}"
    except Exception as e:
        return f"Error retrieving financial information: API might be unavailable. Detail: {str(e)}"
