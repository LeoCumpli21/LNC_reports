
from process_data import *

# Get today's date in format <year-month-day>
# todays_date = datetime.now().strftime("%Y-%m-%d")
todays_date = "2022-11-18"

filename = "data/raw/graph_metrics_" + todays_date + ".json.tar.gz"

# Read graph file
graph_json = decompress_network_graph(filename)

# Get nodes and channels graphs
nodes_graph, channels_graph = to_pandas_df(graph_json)

# Combine channels graph with nodes graph
ln_graph = add_node_chan_info(nodes_graph, channels_graph)

# Drop unnecessary columns
ln_graph = ln_graph.drop([
    col for col in ln_graph.columns if 'features' in col
    ], axis=1)

# Change capacity units to btc
ln_graph = to_btc_units(ln_graph)

# Save graph into csv file in data/processed/... folder
dir = "data/processed"
ln_graph.to_csv(f"{dir}/network_graph_{todays_date}.csv")