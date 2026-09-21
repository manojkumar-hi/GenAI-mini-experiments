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
            return {"principal": p, "rate": annual_rate, "years": duration_years, "emi": f"Rs. {round(emi, 2):,}", "error": None}
            
        emi = p * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
        return {"principal": p, "rate": annual_rate, "years": duration_years, "emi": f"Rs. {round(emi, 2):,}", "error": None}
    except Exception as e:
        return {"error": f"Error calculating EMI: {str(e)}"}

def calculate(expression):
    try:
        match = re.match(r'^\s*([0-9.]+)\s*([\+\-\*\/])\s*([0-9.]+)\s*$', expression)
        if not match:
            return {"error": "Invalid expression. Only basic arithmetic with two numbers is supported (e.g., 25 * 48)."}
        
        num1, op, num2 = float(match.group(1)), match.group(2), float(match.group(3))
        
        ops = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv
        }
        
        if op == '/' and num2 == 0:
            return {"error": "Division by zero."}
            
        result = ops[op](num1, num2)
        
        if result.is_integer():
            return {"result": str(int(result)), "error": None}
        return {"result": str(round(result, 4)), "error": None}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

def get_stock_price(symbol):
    try:
        indian_stocks = ['RELIANCE', 'TCS', 'INFY']
        if symbol.upper() in indian_stocks:
            symbol = symbol.upper() + '.NS'
            
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="1d")
        
        if history.empty:
            if not symbol.endswith('.NS'):
                ticker = yf.Ticker(symbol + ".NS")
                history = ticker.history(period="1d")
                if history.empty:
                    return {"error": f"Could not retrieve price for {symbol}. It might be invalid or delisted."}
                symbol = symbol + ".NS"
            else:
                return {"error": f"Could not retrieve price for {symbol}."}
        
        last_price = history['Close'].iloc[-1]
        currency = "Rs." if symbol.endswith(".NS") or symbol.endswith(".BO") else "$"
        return {"symbol": symbol, "price": f"{currency} {last_price:,.2f}", "error": None}
    except Exception as e:
        return {"error": "The external financial-data service could not be reached right now."}

def get_financial_information(symbol):
    try:
        indian_stocks = ['RELIANCE', 'TCS', 'INFY']
        if symbol.upper() in indian_stocks:
            symbol = symbol.upper() + '.NS'
            
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if 'shortName' not in info and 'longName' not in info:
             if not symbol.endswith('.NS'):
                ticker = yf.Ticker(symbol + ".NS")
                info = ticker.info
                if 'shortName' not in info and 'longName' not in info:
                    return {"error": f"Could not retrieve information for {symbol}."}
                symbol = symbol + ".NS"
             else:
                 return {"error": f"Could not retrieve info for {symbol}."}
             
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
