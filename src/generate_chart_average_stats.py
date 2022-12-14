from generate_charts import *


def plot_med_statistics(f, data1, y1, t_d, date_28_days_ago):
    """
    f: figure where to plot
    data1: network basic stats dataframe
    y1: string
    t_d: current date
    date_28_days_ago: date a month ago
    """

    rc = {
        "axes.grid": True,  # for horizontal lines for each y-axis point
        "grid.color": "#436280",
        "font.size": 20,
    }
    plt.rcParams.update(rc)

    # Set figure background to be transparent
    # f.patch.set_alpha(0)

    ax = f.add_subplot(
        211,
    )
    # ax.patch.set_alpha(0)
    ax2 = f.add_subplot(
        212,
    )
    # ax2.patch.set_alpha(0)
    f.set_facecolor(color="#033048")
    ax.set_facecolor(color="#033048")
    ax2.set_facecolor(color="#033048")

    axes = [ax, ax2]
    for a in axes:
        # Change bottom spine color to be white
        a.spines["bottom"].set_color("#FFFFFF")
        a.tick_params(axis="x", colors="#FFFFFF")
        a.tick_params(axis="y", colors="#FFFFFF")
        # Hide the right, left and top spines
        a.spines["right"].set_visible(False)
        a.spines["left"].set_visible(False)
        a.spines["top"].set_visible(False)
    # remove x tick labels from ax 1
    ax.tick_params(axis="x", labelbottom=False)

    # For the legend
    legend_label1 = " ".join([w.capitalize() for w in y1.split("_")])

    # Choose data from 4 weeks ago till now
    data1 = data1.loc[date_28_days_ago:]

    # Plotting data from 4 weeks ago till 1 week ago
    ax.plot(
        data1.loc[date_28_days_ago : t_d - timedelta(days=6), "date"],  # x axis
        data1.loc[date_28_days_ago : t_d - timedelta(days=6), y1],  # y axis
        label=legend_label1,
        color="#FFFFFF",
    )
    # change y axis label text
    ax.yaxis.label.set_text("Channel size")
    # Plotting this weeks data
    ax.plot(
        data1.loc[t_d - timedelta(days=7) :, "date"],  # x axis
        data1.loc[t_d - timedelta(days=7) :, y1],  # y axis
        color="#4EBEB9",
    )

    # Plotting data from 1 week ago till now
    ax2.plot(
        data1.loc[date_28_days_ago:, "date"],  # x axis
        data1.loc[date_28_days_ago:, "median_channel_size"],  # y axis,
        color="#FFFFFF",
        linestyle="--",
        label="Median Channel Size",
    )

    # change y axis label text
    ax2.yaxis.label.set_text("Channel size")

    # Rotar los ticks del x axis
    ax2.xaxis.set_tick_params(rotation=20)

    # get y ticks and change them
    yticks = ax2.get_yticks()
    ax2.set_yticks([float(f"{x:.3f}") for x in yticks])

    for a in axes:
        # font size of x & y ticks
        a.tick_params(axis="both", which="major", labelsize=16)
        # change y axis label color
        a.yaxis.label.set_color("#FFFFFF")
        # axis legend color
        leg = a.legend(facecolor="#5D89B3", borderpad=0.5)
        for text in leg.get_texts():
            text.set_color("#FFFFFF")

    return
