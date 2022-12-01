import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
from pandas import json_normalize
import json, gzip, tarfile, io
from datetime import datetime
from process_data import decompress_network_graph, to_pandas_df


def get_total_stats(channels_graph, nodes_graph):

    # Network capacity
    network_cap = channels_graph.capacity.sum() / 100000000
    # Total number of channels
    num_channels = channels_graph.shape[0]
    # Total number of nodes
    num_nodes = nodes_graph.shape[0]

    return network_cap, num_channels, num_nodes

def get_avg_stats(network_cap, num_channels, num_nodes):
  # Average channel size
  avg_chan_size = network_cap / num_channels
  # Average node capacity
  avg_node_cap = network_cap / num_nodes

  return avg_chan_size, avg_node_cap

def get_median_stats(channels_graph):
  # Median channel size
  median_chan_size = channels_graph['capacity'].median() / 100000000
  return median_chan_size

def get_todays_network_data(nodes_graph, channels_graph, todays_date):
    network_cap, num_channels, num_nodes = get_total_stats(channels_graph, nodes_graph)
    avg_chan_size, avg_node_cap = get_avg_stats(network_cap, num_channels, num_nodes)
    med_chan_size = get_median_stats(channels_graph)
    # todays network data
    network_data_td = num_nodes, num_channels, network_cap, todays_date, avg_chan_size, avg_node_cap, med_chan_size

    return network_data_td

def load_basic_stats(filename):
    """
    Loads basic stats csv file

    Returns basic stats dataframe
    """
    network_basic_stats = pd.read_csv(
        filename,
        index_col=0
    )
    # drop duplicates in case they are
    network_basic_stats.drop_duplicates(subset='date', keep='first', inplace=True)

    return network_basic_stats

def add_new_network_stats(df, todays_date):
    """
    Saves new stats into csv file

    df: network basic stats dataframe

    returns Nothing
    """
    # add today's network stats
    len_df = df.shape[0]

    filename = "data/raw/graph_metrics_" + todays_date + ".json.tar.gz"

    graph = decompress_network_graph(filename)
    nodes_graph, channels_graph = to_pandas_df(graph)

    network_data_td = get_todays_network_data(nodes_graph, channels_graph, todays_date)
    df.loc[len_df] = network_data_td

    df.to_csv("data/processed/basic_stats/network_basic_stats.csv")
