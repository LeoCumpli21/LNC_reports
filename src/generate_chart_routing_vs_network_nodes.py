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

def fix_routing_nodes_stats(df_1, df_2):
    """
    Subtracts the number of big nodes from routing nodes

    df_1: routing nodes stats df
    df_2: big nodes stats df

    returns df_1 modified
    """

    df_1['routing_nodes'] -= df_2['num_nodes']

    return df_1

def plot_net_statistics(f, data1, data2, y1, y2, t_d, date_28_days_ago):

    rc = {
            'axes.grid' : True, # for horizontal lines for each y-axis point
            'grid.color': '#436280',
            'font.size': 20,
    }
    plt.rcParams.update(rc)

    # Set figure background to be transparent
    # f.patch.set_alpha(0)
    f.set_facecolor(color="#033048")
    ax = f.add_subplot(211)
    ax.set_facecolor(color="#033048")
    # ax.patch.set_alpha(0)
    ax2 = f.add_subplot(212)
    ax2.set_facecolor(color="#033048")
    # ax2.patch.set_alpha(0)

    axes = [ax, ax2]
    for a in axes:
        # Change bottom spine color to be white
        a.spines['bottom'].set_color('#FFFFFF')
        a.tick_params(axis='x', colors='#FFFFFF')
        a.tick_params(axis='y', colors='#FFFFFF')
        # Hide the right, left and top spines
        a.spines['right'].set_visible(False)
        a.spines['left'].set_visible(False)
        a.spines['top'].set_visible(False)
    # remove x tick labels from ax 1
    ax.tick_params(axis='x', labelbottom=False)

    # Create labels for data
    legend_label1 = " ".join([w.capitalize() for w in y1.split('_')])
    legend_label2 = " ".join([w.capitalize() for w in y2.split('_')])

    # choose last 4 weeks
    d1 = data1.loc[date_28_days_ago:]
    d2 = data2.loc[date_28_days_ago:]

    ######## ROUTING NODES #########
    # Plotting data from 4 weeks ago till 1 week ago
    ax.plot(
        data1.loc[date_28_days_ago: date_28_days_ago + timedelta(days=21), "date"], # x axis
        data1.loc[date_28_days_ago: date_28_days_ago + timedelta(days=21), y1], # y axis
        label=legend_label1,
        color='#FFFFFF'
    )
    # y label
    ax.yaxis.label.set_text('Count')

    # Plotting this weeks data
    ax.plot(
        data1.loc[t_d - timedelta(days=7):, "date"], # x axis
        data1.loc[t_d - timedelta(days=7):, y1], # y axis
        color='#4EBEB9'
    )

    ############### NETWORK NODES #########
    # Plotting data from 4 weeks ago till 1 week ago
    ax2.plot(
        # antes era 22
        data2.loc[date_28_days_ago: date_28_days_ago + timedelta(days=21), "date"], # x axis
        data2.loc[date_28_days_ago: date_28_days_ago + timedelta(days=21), y2], # y axis
        label=legend_label2,
        color='#FFFFFF'
    )
    # y label
    ax2.yaxis.label.set_text('Count')
    # Plotting this weeks data
    ax2.plot(
        data2.loc[t_d - timedelta(days=7):, "date"], # x axis
        data2.loc[t_d - timedelta(days=7):, y2], # y axis
        color='#4EBEB9'
    )


    # Rotar los ticks del x axis
    ax2.xaxis.set_tick_params(rotation=20)

    for a in axes:
        # font size of x & y ticks
        a.tick_params(axis='both', which='major', labelsize=16)
        # change y axis label color
        a.yaxis.label.set_color('#FFFFFF')
        # axis legend color
        leg = a.legend(facecolor='#5D89B3', borderpad=0.5)
        for text in leg.get_texts():
            text.set_color("#FFFFFF")
    
    return