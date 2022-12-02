import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.gridspec as gridspec
import matplotlib.image as mimage
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def get_time(todays_date):
    """
    Returns a tuple (date_now, 28_days_ago)
    representing current date and date 28 days ago
    """

    # Using current time
    # t_d = datetime.now()
    t_d = datetime.strptime(todays_date, '%Y-%m-%d') ### THIS IS JUST FOR TESTING
    ### AND SHOULD BE CLEARED OUT LATER
    # 4 weeks ago
    date_28_days_ago = (t_d - timedelta(days = 28))

    return t_d, date_28_days_ago

def cast_df_date(df):
    """
    Casts date column from str to datetime

    df: dataframe of stats with a column named "date"

    returns df
    """

    df.date = pd.to_datetime(df.date)

    return df
    