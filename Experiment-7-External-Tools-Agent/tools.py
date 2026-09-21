import re
import operator
import yfinance as yf
import ast

COMPANY_TICKER_MAP = {
    "apple": "AAPL",
    "reliance industries": "RELIANCE.NS",
    "reliance": "RELIANCE.NS",
    "tata consultancy services": "TCS.NS",
    "tcs": "TCS.NS",
    "infosys": "INFY.NS",
    "infy": "INFY.NS"
}

def resolve_ticker(query):
    """Resolves a company name in a natural language query to its stock ticker."""
    query_lower = query.lower()
    # Sort keys by length descending to match "reliance industries" before "reliance"
    for company in sorted(COMPANY_TICKER_MAP.keys(), key=len, reverse=True):
        if company in query_lower:
            return COMPANY_TICKER_MAP[company]
    return None

def parse_and_calculate_emi(query):
    query_lower = query.lower()
    
    principal = None
    rate = None
    years = None
    
    # Extract "lakh"
    lakh_match = re.search(r'([\d\.]+)\s*lakh', query_lower)
    if lakh_match:
        principal = float(lakh_match.group(1)) * 100000
        
    # Extract explicitly marked parameters
    rate_match = re.search(r'([\d\.]+)\s*%', query_lower)
    if rate_match:
        rate = float(rate_match.group(1))
        
    year_match = re.search(r'([\d\.]+)\s*(year|yr|years)', query_lower)
    if year_match:
        years = float(year_match.group(1))
        
    # Heuristic fallback for unmarked numbers
    nums = [float(x) for x in re.findall(r'\d+(?:\.\d+)?', query_lower)]
    for n in nums:
        # Skip if already matched
        if lakh_match and float(lakh_match.group(1)) == n: continue
        if rate_match and float(rate_match.group(1)) == n: continue
        if year_match and float(year_match.group(1)) == n: continue
        
        if n >= 1000 and principal is None:
            principal = n
        elif n <= 50:
            if rate is None and years is not None:
                rate = n
            elif years is None and rate is not None:
                years = n
            elif rate is None and years is None:
                # If there's a decimal, likely rate
                if '.' in str(n) and not float(n).is_integer():
                    rate = n
                else:
                    years = n

    missing = []
    if principal is None: missing.append("loan amount (principal)")
    if rate is None: missing.append("annual interest rate")
    if years is None: missing.append("duration (years)")
    
    if missing:
        return {
            "error": "I need more information to calculate the EMI. Please provide the: " + ", ".join(missing) + ".",
            "principal": principal,
            "rate": rate,
            "years": years
        }
        
    return calculate_emi(principal, rate, years)


def calculate_emi(principal, annual_rate, duration_years):
    try:
        p = float(principal)
        r = float(annual_rate) / 12 / 100
        n = float(duration_years) * 12
        
        if r == 0:
            emi = p / n if n > 0 else 0
            return {"principal": p, "rate": annual_rate, "years": duration_years, "emi": f"Rs. {round(emi, 2):,}", "error": None}
            
        emi = p * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
        return {"principal": p, "rate": annual_rate, "years": duration_years, "emi": f"Rs. {round(emi, 2):,}", "error": None}
    except Exception as e:
        return {"error": f"Error calculating EMI: {str(e)}"}

def calculate(expression):
    try:
        # Clean up expression (remove trailing punctuation that might break parser)
        expr = expression.strip('.? \t\n\r')
        
        # Safely evaluate math expression using ast
        allowed_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }

        def _eval(node):
            if isinstance(node, ast.Constant): # Python 3.8+ handles Num via Constant
                if isinstance(node.value, (int, float)):
                    return node.value
                raise TypeError("Only numbers are allowed.")
            elif isinstance(node, ast.Num): # Python < 3.8
                return node.n
            elif isinstance(node, ast.BinOp):
                return allowed_operators[type(node.op)](_eval(node.left), _eval(node.right))
            elif isinstance(node, ast.UnaryOp):
                return allowed_operators[type(node.op)](_eval(node.operand))
            else:
                raise TypeError(f"Unsupported syntax: {type(node)}")

        node = ast.parse(expr, mode='eval').body
        result = _eval(node)
        
        if isinstance(result, float) and result.is_integer():
            return {"result": str(int(result)), "error": None}
        return {"result": str(round(result, 4)), "error": None}
        
    except SyntaxError:
        return {"error": "Invalid mathematical expression."}
    except KeyError:
        return {"error": "Unsupported mathematical operator."}
    except ZeroDivisionError:
        return {"error": "Division by zero is not allowed."}
    except Exception as e:
        return {"error": f"Error parsing expression: {str(e)}"}

def get_stock_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="1d")
        
        if history.empty:
            return {"error": f"Could not retrieve price for {symbol}. It might be invalid or delisted."}
        
        last_price = history['Close'].iloc[-1]
        currency = "Rs." if symbol.endswith(".NS") or symbol.endswith(".BO") else "$"
        return {"symbol": symbol, "price": f"{currency} {last_price:,.2f}", "error": None}
    except Exception as e:
        return {"error": "The external financial-data service could not be reached right now."}

def get_financial_information(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if 'shortName' not in info and 'longName' not in info:
             return {"error": f"Could not retrieve information for {symbol}."}
             
        name = info.get('shortName', info.get('longName', 'Unknown'))
        industry = info.get('industry', 'Unknown')
        sector = info.get('sector', 'Unknown')
        market_cap = info.get('marketCap', 'Unknown')
        exchange = info.get('exchange', 'Unknown')
        current_price = info.get('currentPrice', info.get('previousClose', 'Unknown'))
        
        if isinstance(market_cap, (int, float)):
             market_cap = f"{market_cap:,}"
             
        return {
            "name": name,
            "symbol": symbol,
            "exchange": exchange,
            "sector": sector,
            "industry": industry,
            "current_price": current_price,
            "market_cap": market_cap,
            "error": None
        }
    except Exception as e:
        return {"error": "The external financial-data service could not be reached right now."}
