import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def get_time(date: str) -> datetime:
    """
    returns date in datetime type
    """

    # Using current time
    # t_d = datetime.now()
    d = datetime.strptime(date, '%Y-%m-%d') ### THIS IS JUST FOR TESTING
    ### AND SHOULD BE CLEARED OUT LATER
    # 4 weeks ago
    # date_28_days_ago = (t_d - timedelta(days = 27))

    return d

def cast_df_date(df):
    """
    Casts date column from str to datetime

    df: dataframe of stats with a column named "date"

    returns df
    """

    df.date = pd.to_datetime(df.date)

    return df
    