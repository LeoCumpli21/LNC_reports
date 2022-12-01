
from process_data import *
from save_basic_stats import load_basic_stats, add_new_network_stats, save_routing_nodes_stats
from save_basic_stats import save_big_nodes_stats

# Get today's date in format <year-month-day>
todays_date = datetime.now().strftime("%Y-%m-%d")
# todays_date = "2022-11-18" ### THIS IS JUST FOR TESTING 

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
dir = "data/processed/graphs"
ln_graph.to_csv(f"{dir}/network_graph_{todays_date}.csv")

### NETWORK basic stats
# Load basic stats csv
net_stats_filename = "data/processed/basic_stats/network_basic_stats.csv"
network_basic_stats = load_basic_stats(net_stats_filename)
# Save new basic stats
add_new_network_stats(network_basic_stats, todays_date)

#### Stats of ROUTING NODES 
# network's csv graph file
net_csv = "data/processed/graphs/network_graph_" + todays_date + ".csv"
# routing nodes stats csv file
routing_stats_file = "data/processed/basic_stats/routing_nodes_stats.csv"
# Save new routing nodes stats
save_routing_nodes_stats(net_csv, routing_stats_file, todays_date)

# BIG NODES stats
big_stats_file = "data/processed/basic_stats/big_nodes_stats.csv"
# Save new big nodes stats
save_big_nodes_stats(net_csv, big_stats_file, todays_date)