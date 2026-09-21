# Experiment 7 CO3
## AI Agent Using External Tools

## Aim
To create an AI agent that can intelligently select and use external tools to fulfill user requests, rather than attempting to answer all queries from its own static knowledge base.

## Case Study
A financial assistant agent capable of calculating loan EMIs, performing arithmetic calculations, retrieving stock prices, and fetching financial company information using external APIs and dedicated python functions.

## Objectives
- Build an agent that acts as a router to select the right tool based on the user's intent.
- Implement an EMI calculation tool.
- Implement a safe arithmetic calculation tool without using unrestricted `eval()`.
- Integrate an external public API (`yfinance`) to fetch live stock prices and company financial information.
- Provide a clean Streamlit interface to demonstrate the architecture.

## Technologies Used
- **Python**: Core logic.
- **Streamlit**: User interface.
- **yfinance**: Free, public, and open-source library that queries the Yahoo Finance API for market data without requiring API keys.

## System Architecture
The application works by routing natural language queries through a decision engine (rule-based for this experiment) to determine the appropriate tool.
```text
User Query
    ↓
Agent / Tool Selection
    ↓
┌──────────────┬──────────────┬────────────────┐
↓              ↓              ↓                ↓
EMI Tool   Calculator Tool  Stock Price   Financial Info
└──────────────┴──────────────┴────────────────┘
                     ↓
               Tool Result
                     ↓
              Agent Response
```

## Available Tools

### EMI Calculator
Calculates the monthly EMI given the principal amount, annual interest rate, and duration in years. Handles the mathematical formula directly.

### General Calculator
Safely parses and computes basic arithmetic operations (`+`, `-`, `*`, `/`) between two numbers. It deliberately avoids using the unsafe `eval()` function to prevent arbitrary code execution vulnerabilities.

### Stock Price Tool
Uses `yfinance` to request the latest market price of a given ticker symbol. It supports Indian stock symbols (by appending `.NS` when required) as well as global symbols like `AAPL`.

### Financial Information Tool
Uses `yfinance` to fetch metadata about a publicly traded company, including its industry, market capitalization, and a brief business summary.

## How Tool Selection Works
In this academic implementation, a rule-based natural language matching system is used. 
- Queries containing "emi" route to the EMI Calculator.
- Queries starting with "calculate" followed by math operators route to the General Calculator.
- Queries containing "stock" or "price" route to the Stock Price Tool.
- Queries asking for "financial information" route to the Financial Information Tool.

## Project Structure
```text
Experiment-7-External-Tools-Agent/
│
├── app.py              # Streamlit interface and tool router
├── tools.py            # External tool implementations (EMI, Math, Stock, Info)
├── requirements.txt    # Required python packages
├── README.md           # Documentation
└── .gitignore          # Ignored files
```

## Installation
1. Navigate to the project directory:
   ```bash
   cd Experiment-7-External-Tools-Agent
   ```
2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
No API keys or configuration files are required for this project. It relies on the free `yfinance` library which queries Yahoo Finance publicly without requiring authentication.

## How to Run
Run the Streamlit application using:
```bash
streamlit run app.py
```

## Example Interactions
1. **EMI**: 
   - *User:* "Calculate EMI for a loan of 500000 at 8.5% for 5 years."
   - *Agent selects:* EMI Calculator
   - *Result:* Monthly EMI: ₹10,259.24

2. **Calculator**:
   - *User:* "Calculate 25 * 48."
   - *Agent selects:* General Calculator
   - *Result:* Result: 1200

3. **Stock Price**:
   - *User:* "What is the current price of RELIANCE?"
   - *Agent selects:* Stock Price Tool
   - *Result:* Current/last closing price of RELIANCE.NS is ₹[live price]

4. **Financial Information**:
   - *User:* "Give me financial information about TCS."
   - *Agent selects:* Financial Information Tool
   - *Result:* [Company name, industry, market cap, and summary]

## Testing
- The arithmetic parser safely handles inputs without `eval`.
- The EMI calculation applies standard compound interest formulas safely preventing division by zero.
- The `yfinance` API calls include `try/except` blocks to gracefully handle network failures or invalid stock tickers.

## Limitations
- Market data fetched via `yfinance` may be delayed depending on the exchange.
- The tool selector is rule-based and may not catch complex phrasing that a production LLM agent would.
- If Yahoo Finance changes its undocumented API, `yfinance` might temporarily fail to fetch data. Error handling is present to inform the user if this occurs.

## Expected Result
A functional Streamlit application that visibly proves the separation between the agent (router) and its tools, successfully answering queries by delegating work to dedicated python functions or external APIs.

## Conclusion
This experiment successfully demonstrates the architectural concept of Tool Use (Function Calling) in AI agents. By integrating calculation functions and external network requests into the agent's workflow, the agent overcomes the limitations of static knowledge bases.
