from generate_charts import *


def get_capacities(network_stats, routing_stats, big_stats, big_nodes, date):
    """
    network_stats: network basic stats dataframe
    routing_stats: routing nodes stats dataframe
    big_stats: big nodes stats dataframe
    big_nodes: cleaned big nodes description dataframe

    returns (networks capacity, routing nodes capacity, big nodes capacity)
    """

    # get the capacoty of the big routing nodes ( > 40 btc that
    # are categorized as routing nodes)

    big_rn_cap = big_nodes[
        big_nodes["type"] == "Routing Node"
    ].total_capacity.sum()
    # get nodes capacities
    rn_total_cap_2 = (
        routing_stats.loc[date, "total_capacity"]
        - big_stats.loc[date, "total_capacity"]
        + big_rn_cap
    )
    big_nodes_total_cap = big_stats.loc[date, "total_capacity"] - big_rn_cap
    ln_total_cap_2 = (
        (network_stats.loc[date, "total_capacity"]) * 2
        - rn_total_cap_2
        - big_nodes_total_cap
    )

    return ln_total_cap_2, rn_total_cap_2, big_nodes_total_cap


def plot_capacities_pie(f, net_cap, rn_cap, big_cap):
    """
    Plots the network's capacity distribution in a pie chart

    f: matplotlib figure
    net_cap: networks capacity without routing and big nodes
    rn_cap: routing nodes capacity
    big_cap: industrial nodes capacity
    """

    rc = {
        "axes.grid": True,  # for horizontal lines for each y-axis point
        "grid.color": "#436280",
        "font.size": 20,
    }
    plt.rcParams.update(rc)

    ax = f.add_subplot(111)
    # set figure background color
    f.set_facecolor(color="#033048")
    ax.set_facecolor(color="#033048")

    _, texts, autotexts = plt.pie(
        [rn_cap, net_cap, big_cap],
        labels=["Routing Nodes", "Rest of Nodes", "Big Nodes"],
        colors=["#5D89B3", "#436280", "#FFFFFF"],
        autopct="%1.1f%%",
    )
    # for the text inside the pie
    for i, autotext in enumerate(autotexts):
        if i == 2:
            autotext.set_color("black")
        else:
            autotext.set_color("#FFFFFF")
    # for text of labels
    for text in texts:
        text.set_color("#FFFFFF")
