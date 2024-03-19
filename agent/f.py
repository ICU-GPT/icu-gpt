import pandas as pd
from typing_extensions import Annotated
from sqlalchemy import Engine

def run_sql(sql:Annotated[str,'Need to execute SQL'],conn:Engine,data:pd.DataFrame,show_sql:bool = True):
    if show_sql:
        print(sql)
    data = pd.read_sql_query(sql,conn)
    return data

