import pandas as pd
from datetime import datetime as dt, date, time
from dateutil.relativedelta import relativedelta
import urllib
import json
import requests

url_walcl = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=WALCL&cosd={}"
url_rem = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=RESPPLLOPNWW&cosd={}"
url_spx = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500&cosd={}"
url_tga = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/dts_table_1?filter=record_date:gte:{},account_type:eq:Treasury%20General%20Account%20(TGA)%20Opening%20Balance&fields=record_date,open_today_bal&page[number]=1&page[size]=900"
url_rrp = "https://markets.newyorkfed.org/api/rp/reverserepo/propositions/search.json?startDate={}"
class CustomError(Exception):
    "Raised when an API call raises an Error"
    pass

class NetLiquidityCalculation:
    def __init__(self, start_date):
        self.start_date = start_date
        self.walcl = self.get_csvs(url_walcl, "WALCL") * 1_000_000
        self.rem = self.get_csvs(url_rem,"REM") * 1_000_000
        self.spx = self.get_csvs(url_spx,"SPX")

        self.tga = self.get_tga()
        self.rrp = self.get_rrp()
        self.rrp = self.rrp.loc[self.rrp["RRP"] != 0]

    @staticmethod
    def check_api(response, api_content):
        try:
            if response.status_code == 200:
                json_data = response.json()
            else:
                raise CustomError
        except:
            print(f"Failed to retrieve data from the {api_content} API.")
            raise Exception
        return json_data

    def get_csvs(self, url, name):
        url = url.format(self.start_date)
        try:
            df = pd.read_csv(url, index_col=0, parse_dates=True, date_format="%Y-%m-%d")
        except:
            print("Failed to retrieve data from the CSV API.")
            raise Exception
        df.columns = [name]

        df[name] = pd.to_numeric(df[name], errors='coerce')
        return df
    def get_tga(self):
        url = url_tga.format(self.start_date)
        response = requests.get(url)
        json_data = self.check_api(response, "TGA")

        df = pd.DataFrame(json_data["data"]).set_index("record_date")
        df.columns = ["TGA"]
        df["TGA"] = df["TGA"].astype("float32")
        df.index = pd.to_datetime(df.index, format="%Y-%m-%d")
        return df * 1000 * 1000

    def get_rrp(self):
        url = url_rrp.format(self.start_date)
        response = requests.get(url)
        json_data = self.check_api(response, "RRP")

        # use of propositions key (json_data["repo"]["operations"][i] could allow breakdown by counterparty however that is irrelevant to me for the moment
        df = pd.DataFrame(json_data["repo"]["operations"])[["operationDate", "totalAmtAccepted"]].set_index("operationDate")
        df.columns = ["RRP"]
        df.index = pd.to_datetime(df.index, format="%Y-%m-%d")
        return df.sort_index()

    def calculate_net_liquidity(self):
        df = self.rrp.join(self.walcl).join(self.tga).join(self.rem).join(self.spx)
        df = df.ffill()
        df["NL"] = df["WALCL"] - df[["TGA", "REM", "RRP"]].sum(axis=1)
        df["SPX_FV"] = df["NL"] / 1_000_000_000 / 1.1 - 1625
        df["SPX_HI"] = df["SPX_FV"] + 300
        df["SPX_LO"] = df["SPX_FV"] - 200
        df = df.dropna(how="any")
        df = df.loc[df["RRP"] != 0]
        return df

if __name__ == '__main__':
    NetLiquidityCalculation(date(2023,7,1)).calculate_net_liquidity()

