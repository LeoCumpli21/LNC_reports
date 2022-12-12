from generate_charts import *


def get_big_routing_nodes_data(big_nodes, date):
    """
    big_nodes: cleaned big nodes dataframe
    date: date 28 days ago

    returns a list with the big routing nodes accumulated capacity
    in chronological order
    """

    big_rn = big_nodes[big_nodes["type"] == "Routing Node"]
    # Public keys of big routing nodes
    big_rn_pk = big_rn.pub_key.values

    big_rn_capacities = []

    # Get data of big routing nodes
    for _ in range(28):
        date = date.strftime("%Y-%m-%d")
        # load networks graph

        graph_file = f"data/processed/graphs/network_graph_{date}.csv"

        try:
            ln_graph = pd.read_csv(graph_file, index_col=0)
        except:
            print(f"{date} not found")
            date = pd.to_datetime(date)
            date += timedelta(days=1)
            continue
        # query graph for public keys
        big_rn_total_cap = ln_graph[
            ln_graph["pub_key"].isin(big_rn_pk)
        ].total_capacity.sum()
        big_rn_capacities.append(big_rn_total_cap)

        date = pd.to_datetime(date)
        date += timedelta(days=1)

    return big_rn_capacities


def get_nodes_capacities(
    network_stats, rn_stats, big_stats, date, big_rn_capacities
):

    """
    Gets the accumulated capacity of the 3 node categories, and returns them.

    network_stats: network basic stats dataframe
    rn_stats: routing nodes stats dataframe
    big_stats: big nodes stats dataframe
    date: date 28 days ago
    big_rn_capacities: daily accumulated capacities of the big routing nodes
        from 28 days ago till now

    returns a tupple:
        (x, y1, y2, y3), where x are dates, and the y's are nodes capacities
    """

    routing_nodes_stats = rn_stats.loc[date:]
    big_nodes_stats = big_stats.loc[date:]
    network_basic_stats = network_stats.loc[date:]

    # subtracting big nodes stats from routing nodes stats, so that we
    # have stats for nodes with 1 < btc < 40
    rou_nodes_sts = (
        routing_nodes_stats[["total_capacity", "num_channels"]]
        - big_nodes_stats[["total_capacity", "num_channels"]]
    )
    rou_nodes_sts = rou_nodes_sts.total_capacity + big_rn_capacities

    # big nodes stats
    big_nodes_cap = big_nodes_stats.total_capacity - big_rn_capacities
    # subtract from net stats big nodes and routing nodes to get the rest
    rest_nodes = (
        network_basic_stats["total_capacity"] * 2
        - rou_nodes_sts
        - big_nodes_cap
    )

    return (
        big_nodes_stats.date.values,
        rest_nodes.values,
        rou_nodes_sts.values,
        big_nodes_cap.values,
    )


def plot_area_capacities_chart(fig, x, y1, y2, y3):

    # plt.fill_between(x,y1)
    rc = {
        "axes.grid": True,  # for horizontal lines for each y-axis point
        "grid.color": "#436280",
        "font.size": 20,
    }
    plt.rcParams.update(rc)

    ax = fig.add_subplot(111)
    # set background color
    fig.set_facecolor(color="#033048")
    ax.set_facecolor(color="#033048")

    # Change bottom spine color to be white
    ax.spines["bottom"].set_color("#FFFFFF")
    ax.tick_params(axis="x", colors="#FFFFFF")
    ax.tick_params(axis="y", colors="#FFFFFF")
    # Hide the right, left and top spines
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["top"].set_visible(False)

    ax.fill_between(x, y2, label="Routing nodes", color="#5D89B3")
    ax.fill_between(x, y3, label="Big nodes", color="#FFFFFF")
    ax.fill_between(x, y1, label="Rest of nodes", color="#b6dcff")
    ax.xaxis.set_tick_params(rotation=20)
    # plt.stackplot(x, y3, y2)
    ax.legend(loc="upper left")

    return
