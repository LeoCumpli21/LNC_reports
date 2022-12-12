from process_data import *
from save_basic_stats import add_new_network_stats, save_routing_nodes_stats
from save_basic_stats import save_big_nodes_stats
from save_basic_stats import (
    load_network_basic_stats,
    load_big_nodes_stats,
    load_routing_nodes_stats,
)
from generate_chart_routing_vs_network_nodes import *
from generate_chart_total_stats import plot_net_statistics
from generate_chart_average_stats import plot_med_statistics
from generate_chart_big_nodes_categories_pie import *
from generate_chart_networks_capacity_distr import *
from generate_chart_nodes_categories import *
from generate_chart_stacked_area import *

# Get today's date in format <year-month-day>
todays_date = datetime.now().strftime("%Y-%m-%d")
# todays_date = "2022-12-05"  ### THIS IS JUST FOR TESTING

filename = "data/raw/graph_metrics_" + todays_date + ".json.tar.gz"

# Read graph file
graph_json = decompress_network_graph(filename)

# Get nodes and channels graphs
nodes_graph, channels_graph = to_pandas_df(graph_json)

# Combine channels graph with nodes graph
ln_graph = add_node_chan_info(nodes_graph, channels_graph)

# Drop unnecessary columns
ln_graph = ln_graph.drop(
    [col for col in ln_graph.columns if "features" in col], axis=1
)

# Change capacity units to btc
ln_graph = to_btc_units(ln_graph)

# Save graph into csv file in data/processed/... folder
dir = "data/processed/graphs"
ln_graph.to_csv(f"{dir}/network_graph_{todays_date}.csv")

### NETWORK basic stats
# Load basic stats csv
net_stats_filename = "data/processed/basic_stats/network_basic_stats.csv"
network_basic_stats = load_network_basic_stats(net_stats_filename)
# Save new basic stats
add_new_network_stats(network_basic_stats, todays_date)

#### Stats of ROUTING NODES
# network's csv graph file
net_csv = "data/processed/graphs/network_graph_" + todays_date + ".csv"
# routing nodes stats csv file
routing_stats_file = "data/processed/basic_stats/routing_nodes_stats.csv"
# Save new routing nodes stats
save_routing_nodes_stats(net_csv, routing_stats_file, todays_date)

### BIG NODES stats
big_stats_file = "data/processed/basic_stats/big_nodes_stats.csv"
# Save new big nodes stats
save_big_nodes_stats(net_csv, big_stats_file, todays_date)

### CREATING CHARTS ###

### Routing vs network nodes chart
network_basic_stats = load_network_basic_stats(net_stats_filename)
routing_nodes_stats = load_routing_nodes_stats(routing_stats_file)
big_nodes_stats = load_big_nodes_stats(big_stats_file)

# Cast date column of our dataframes from str to date time
network_basic_stats = cast_df_date(network_basic_stats)
routing_nodes_stats = cast_df_date(routing_nodes_stats)
big_nodes_stats = cast_df_date(big_nodes_stats)

data1 = routing_nodes_stats.set_index("date", drop=False)
data2 = network_basic_stats.set_index("date", drop=False)

# get todays date and date 28 days ago
t_d, date_28_ago = get_time(todays_date)

# Create figure
f = plt.figure(figsize=(16, 9))
# plot
plot_routing_vs_net_statistics(
    f, data1, data2, "routing_nodes", "total_nodes", t_d, date_28_ago
)
# Save figure to charts folder
f.savefig(
    f"charts/routing_vs_net_nodes/routing_nodes_stats_{todays_date}_num_nodes.png",
    facecolor="#033048",
)

### Network basic stats charts
# Features to plot
features = ["total_channels", "total_capacity", "total_nodes"]

for f in features:
    # Creates figure
    fig = plt.figure(figsize=(16, 9))
    plot_net_statistics(fig, data2, f, t_d, date_28_ago)
    # figures.append(bar)
    fig.savefig(
        f"charts/total_stats/network_stats_{todays_date}_{f}.png",
        facecolor="#033048",
    )

# For average node capacity
f = plt.figure(figsize=(16, 9))
# Network basic statistics -> data2
plot_net_statistics(
    f,
    data2[["date", "avg_node_capacity"]],
    "avg_node_capacity",
    t_d,
    date_28_ago,
)
# Save chart
f.savefig(
    f"charts/average_stats/avg_node_capacity_{todays_date}.png",
    facecolor="#033048",
)

### Average stats chart
f = plt.figure(figsize=(16, 9))
# Network basic stats : data2
# average channel size
plot_med_statistics(
    f,
    data2[["date", "avg_channel_size", "median_channel_size"]],
    "avg_channel_size",
    t_d,
    date_28_ago,
)
# Save chart
f.savefig(
    f"charts/average_stats/avg_chan_size_{todays_date}.png", facecolor="#033048"
)

### Pie charts
# Big nodes categories distribution pie chart
# load big nodes description
big_nodes = pd.read_csv(
    "data/processed/basic_stats/big_nodes_desc.csv", index_col=0
)
# Clean big nodes df, and get industrial nodes only (exlcuding routing nodes)
big_nodes, industrial_nodes = clean_big_nodes(big_nodes)
# Get big nodes categories distribution
categories_distr = get_big_nodes_distribution(industrial_nodes)
# create figure
f = plt.figure(figsize=(16, 9))
# Plot pie chart
plot_big_nodes_distribution(f, categories_distr)
# Save chart
f.savefig(
    f"charts/pie_charts/big_nodes_pie_{todays_date}.png", facecolor="#033048"
)

# Network's capacity distribution pie chart
# get nodes capacities
ln_total_cap, rn_total_cap, big_total_cap = get_capacities(
    network_basic_stats, routing_nodes_stats, big_nodes_stats, big_nodes
)
# Create figure
f = plt.figure(figsize=(16, 9))
# plot pie chart
plot_capacities_pie(f, ln_total_cap, rn_total_cap, big_total_cap)
# Save figure
f.savefig(
    f"charts/pie_charts/capacity_distribution_{todays_date}.png",
    facecolor="#033048",
)

# Nodes categories pie chart
# get number of nodes of each category
rn_count, rest_count, big_count = get_nodes_count(
    network_basic_stats, routing_nodes_stats, big_nodes_stats
)
# Create figure
f = plt.figure(figsize=(16, 9))
# Plot chart
plot_nodes_categories(f, rn_count, rest_count, big_count)
# Save figure
f.savefig(
    f"charts/pie_charts/share_nodes_pie_{todays_date}.png",
    facecolor="#033048",
)

### AREA CHART
# Get big routing nodes accumulated capacity from 28 days
# ago until now
big_rn_capacities = get_big_routing_nodes_data(big_nodes, date_28_ago)
# get accumulated capacity of routing nodes, big nodes and the rest
x, y_1, y_2, y_3 = get_nodes_capacities(
    data2,
    data1,
    big_nodes_stats.set_index("date", drop=False),
    date_28_ago,
    big_rn_capacities,
)
# Create figure
f = plt.figure(figsize=(16, 9))
# Plot area chart
plot_area_capacities_chart(f, x, y_1, y_2, y_3)
f.savefig(
    f"charts/area_charts/stacked_area_chart_{todays_date}.png",
    facecolor="#033048",
)
