from generate_charts import *


def get_nodes_count(network_stats, rn_stats, big_stats, date):
    """
    network_stats: network basic stats dataframe
    rn_stats: routing nodes stats dataframe
    big_stats: big nodes stats dataframe
    returns (rn count, resto of nodes count, big nodes count)
    """

    # Number of routing nodes
    num_r_nodes = (rn_stats.routing_nodes - big_stats.num_nodes).loc[date]
    # Total nodes in network
    total_n = network_stats.total_nodes.loc[date]
    num_big = big_stats.num_nodes.loc[date]
    # rest of nodes
    num_rest_nodes = total_n - num_r_nodes - num_big

    return num_r_nodes, num_rest_nodes, num_big


def plot_nodes_categories(f, rn_count, rest_count, big_count):

    rc = {
        "axes.grid": True,  # for horizontal lines for each y-axis point
        "grid.color": "#436280",
        "font.size": 20,
    }
    plt.rcParams.update(rc)

    ax = f.add_subplot(111)
    # Set figure's background color
    f.set_facecolor(color="#033048")
    ax.set_facecolor(color="#033048")

    _, texts, autotexts = plt.pie(
        [rn_count, rest_count, big_count],
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

    return
