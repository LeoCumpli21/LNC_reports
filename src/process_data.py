import numpy as np
import pandas as pd
import json, gzip, tarfile, io
from pandas import json_normalize
from datetime import datetime


# Read the compressed channel graph file
# Decompress the gzip
def decompress_network_graph(filename):
    with open(filename, "rb") as f:
        tserial = gzip.decompress(f.read())

    ## Read the Tarfile
    with tarfile.open(fileobj=io.BytesIO(tserial), mode="r") as f:
        fname = [e for e in f.getnames() if e.lower().endswith(".json")][0]
        serial = f.extractfile(fname).read()

    jdata = serial.decode("utf-8")

    # Load as JSON
    graph_json = json.loads(jdata)

    return graph_json


def to_pandas_df(graph):
    """
    Generates pandas dataframes of the graph's data

    graph: networks graph in json format

    Returns nodes and channels dfs
    """
    # Converting data to pd dfs
    nodes_graph = json_normalize(graph["nodes"])
    channels_graph = json_normalize(graph["edges"])
    channels_graph.channel_id = channels_graph.capacity.astype(int)
    channels_graph.capacity = channels_graph.capacity.astype(int)

    return nodes_graph, channels_graph


def add_node_chan_info(df_nodes, df_channels):
    """
    Puts info from channels graph to the nodes graph

    df_nodes:  nodes graph
    df_channels: channels graph

    returns nodes graph datafram updated
    """

    df_nodes = pd.concat(
        [df_nodes, pd.DataFrame(columns=["num_channels", "total_capacity"])],
        sort=False,
    )

    for index, node in df_nodes.iterrows():

        pub_key = node["pub_key"]
        # obtain those channels that were opened by this specific node
        node1_channels = df_channels[df_channels.node1_pub == pub_key]

        # obtain those channels that were opened by other nodes
        node2_channels = df_channels[df_channels.node2_pub == pub_key]

        # for channels
        df_nodes.loc[index, "num_channels"] = (
            node1_channels.shape[0] + node2_channels.shape[0]
        )
        # for capacity
        df_nodes.loc[index, "total_capacity"] = (
            node1_channels.capacity.sum() + node2_channels.capacity.sum()
        )

    return df_nodes


def to_btc_units(df):
    """
    Changes capacity units from sats to btc units

    df: ln graph

    returns df
    """

    df.total_capacity = df["total_capacity"].astype("float64")
    df.num_channels = df["num_channels"].astype("int32")
    # convert total capacity to btc units
    df["total_capacity"] = df["total_capacity"] / 100000000

    return df
