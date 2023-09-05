To run:
- Create a virtual environment
- pip install requirements.txt in said venv
- Run frontend.py

APIs Used:

JSON:
- [TGA](https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/dts_table_1?filter=record_date:gte:2023-01-01,account_type:eq:Treasury%20General%20Account%20(TGA)%20Opening%20Balance&fields=record_date,open_today_bal&page[number]=1&page[size]=900)
- [RRP](https://markets.newyorkfed.org/api/rp/reverserepo/propositions/search.json?startDate=2023-01-01)

CSV:
- [WALCL](https://fred.stlouisfed.org/graph/fredgraph.csv?id=WALCL&cosd=2023-01-01) Total Assets (Less Eliminations from Consolidation)
- [WSHOSHO](https://fred.stlouisfed.org/graph/fredgraph.csv?id=WSHOSHO&cosd=2023-01-01) Securities Held Outright
- [RESPPLLOPNWW / REM](https://fred.stlouisfed.org/graph/fredgraph.csv?id=RESPPLLOPNWW&cosd=2023-01-01) Earnings Remittances Due to the U.S. Treasury
- [SPX Value](https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500&cosd=2023-01-01)

## Net Liquidity Explanation

I found out about using net liquidity to predict the fair value of the S&P500 from https://twitter.com/dharmatrade and Michael Howell at https://twitter.com/crossbordercap

A brief overview:
- Since July 2020, more than the FFR or the Fed Balance Sheet, Liquidity is what really matters in the post-pandemic world. 
- SPX fell into a near-perfect 95% inverse correlation with TGA balance
- To try and such liquidity out of the system, namely:
- Issuing less short-dated T Bills, creating a shortage of risk-free short duration papers
- Raising rates on Reverse Repo, providing a better alternative for low-duration risk

The effects of this are:
- $2 trillion in liquidity was sucked in, with RRP increasing six-fold, which is all money unavailable to circulate in the economy

REM is the Federal Reserves operating losses (Earnings Remittances due to the US Treasury): https://fred.stlouisfed.org/series/RESPPLLOPNWW
This gets us to the equation:
### Net Liquidity = Fed Balance Sheet Size - Funds sucket into treasury (TGA) - Funds in RRP - REM

Reason why Net Liquidity has suddenly emerged as a clear leader in predicting fair value is that TGA and RRP has increased massively during the monetary tightening cycle

