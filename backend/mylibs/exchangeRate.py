import requests
from dataclasses import dataclass
from typing import Union, List, Optional
import pandas as pd
from datetime import datetime

class ExchangeRateError(Exception):
    pass

@dataclass
class ExchangeRate():
    base_url = "https://www.frankfurter.app/"

    @staticmethod
    def convert(targets_codes: Union[str, List[str]], base_code: str = 'EUR', date_from: Optional[str] = None, date_to: Optional[str] = None, amount: int = 1) -> pd.DataFrame:
        '''Date format must be YYYY-MM-DD'''
        if not date_to:
            date_to = datetime.now().strftime("%Y-%m-%d")        
        if date_from: # from date to date/now
            date_to_year = int(date_to[:4])
            date_from_year = int(date_from[:4])
            prefixes = []
            prefixes.append(date_from+".."+str(date_from_year)+'-12-31')
            for year in range(date_from_year+1, date_to_year):
                prefixes.append(str(year)+'-01-01'+'..'+str(year)+'-12-31')
            prefixes.append(str(date_to_year)+'-01-01'+".."+date_to)
        elif date_to: # only specified date
            prefixes = [date_to]
        else: # only now
            prefixes = ['latest']

        if isinstance(targets_codes, str):
            targets_codes = [targets_codes]

        gbx = False
        if "GBX" in targets_codes:
            targets_codes = list(map(lambda x: x.replace('GBX','GBP'), targets_codes))
            gbx = True

        params = {
            'from': base_code,
            'to': ",".join(targets_codes),
            'amount': amount
        }
        dfs = []
        for prefix in prefixes:
            df = ExchangeRate._fetch_data(prefix, params)
            dfs.append(df)
        full_df = pd.concat(dfs)
        if gbx:
            full_df['GBX'] = full_df['GBP']*100
        return full_df

    @staticmethod
    def _fetch_data(prefix, params):
        try:
            response = requests.get(url=ExchangeRate.base_url+prefix, params=params)
            data = response.json()
        except Exception as e:
            raise ExchangeRateError(f"Error accessing exchange rate: {e} with pair {params['from']}/{params['to']} - {response}")

        error = data.get('message')
        if error:
            raise ExchangeRateError(f"Errror with pair {params['from']}/{params['to']}: {error}")
        try:
            date = data.get('date')
            if date:
                df = pd.DataFrame(data['rates'], index=[date])
            else:
                df  = pd.DataFrame.from_dict(data['rates'], orient='index')
        except Exception as e:
            raise ExchangeRateError(f"Error parsing rates with pair {params['from']}/{params['to']} on section {prefix} : {e}")
        return df