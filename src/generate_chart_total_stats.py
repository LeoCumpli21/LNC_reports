from generate_charts import *


def plot_net_statistics(f, data, y, t_d, date_28_days_ago):
    """
    Creates and saves a plot about network basic statistics

    f: matplotlib figure
    data: network stats dataframe
    y: feature to plot (capacity, nodes, or channels)
    """

    rc = {
        "axes.grid": True,  # for horizontal lines for each y-axis point
        "grid.color": "#436280",
        "font.size": 20,
    }
    plt.rcParams.update(rc)

    # Set figure background to be transparent
    # f.patch.set_alpha(0)
    ax = f.add_subplot(111)
    # ax.patch.set_alpha(0)
    # Set background to blue
    f.set_facecolor(color="#033048")
    ax.set_facecolor(color="#033048")

    # Change bottom spine color to be white
    ax.spines["bottom"].set_color("#FFFFFF")
    ax.tick_params(axis="x", colors="#FFFFFF")
    ax.tick_params(axis="y", colors="#FFFFFF")
    # Hide the right, left and top spines
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["top"].set_visible(False)

    legend_label = " ".join([w.capitalize() for w in y.split("_")])

    # choose last 4 weeks data
    data1 = data.loc[date_28_days_ago:]

    # Plotting data from 4 weeks ago till 1 week ago
    ax.plot(
        data1.loc[date_28_days_ago : t_d - timedelta(days=6), "date"],  # x axis
        data1.loc[date_28_days_ago : t_d - timedelta(days=6), y],  # y axis
        label=legend_label,
        color="#FFFFFF",
    )
    # Plotting this weeks data
    ax.plot(
        data1.loc[t_d - timedelta(days=7) : t_d, "date"],  # x axis
        data1.loc[t_d - timedelta(days=7) : t_d, y],  # y axis
        color="#4EBEB9",
    )

    # Rotar los ticks del x axis
    ax.xaxis.set_tick_params(rotation=20)

    # font size of x & y ticks
    ax.tick_params(axis="both", which="major", labelsize=16)
    # change y axis label color
    ax.yaxis.label.set_color("#FFFFFF")
    # axis legend color
    leg = ax.legend(facecolor="#5D89B3", borderpad=1)
    for text in leg.get_texts():
        text.set_color("#FFFFFF")

    return
