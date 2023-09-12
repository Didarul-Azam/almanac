import pandas as pd

class Read_csv:
  
    def __init__(self, filename, date_format="%Y-%m-%d", date_index_name="index"):
        self.filename = filename
        self.date_format = date_format
        self.date_index_name = date_index_name

    def pd_readcsv(self) -> pd.DataFrame:
        ans = pd.read_csv(self.filename)
        ans.index = pd.to_datetime(ans[self.date_index_name], format=self.date_format).values

        del ans[self.date_index_name]

        ans.index.name = None

        return ans
