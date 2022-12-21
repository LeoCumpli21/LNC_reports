from process_data import *
from save_basic_stats import add_new_network_stats, save_routing_nodes_stats
from save_basic_stats import save_big_nodes_stats
from save_basic_stats import (
    load_network_basic_stats,
    load_big_nodes_stats,
    load_routing_nodes_stats,
)
from generate_chart_routing_vs_network_nodes import *
from generate_chart_total_stats import plot_net_statistics, plot_btc_vs_usd_cap
from generate_chart_average_stats import plot_med_statistics
from generate_chart_big_nodes_categories_pie import *
from generate_chart_networks_capacity_distr import *
from generate_chart_nodes_categories import *
from generate_chart_stacked_area import *
import time
import sys


def check_invalid_date(date_string: str) -> bool:

    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return False
    except ValueError as e:
        print(e)
        return True


def ask_for_date() -> str:

    msg = """
    Enter a date in the following format:
        yyyy-mm-dd\n\t
    """

    date = input(msg)
    while check_invalid_date(date):
        print("Invalid date\n")
        date = input(msg)

    return date


def ask_for_pair_of_dates():

    print("Choose from when you want your chart to start")
    starting_d = ask_for_date()
    print("\nNow choose the limit of your chart (could be today)")
    ending_d = ask_for_date()
    # get todays date and date 28 days ago
    start, end = get_time(starting_d), get_time(ending_d)

    return start, end


def validate_pair_of_dates(date_1: datetime, date_2: datetime) -> bool:

    return (date_2 - date_1).days >= 7


def check_invalid_choice(choice, menu=False) -> bool:

    possible_choices = {1, 2, 3, 4, 5}
    if menu:
        possible_choices = {1, 2}

    try:
        choice = int(choice)
    except ValueError:
        return True

    if choice not in possible_choices:
        return True
    return False


def ask_for_chart() -> int:

    print("Which charts do you want to generate?")
    msg = """
    1. Network total stats charts (ex. total channels)
    2. Routing nodes vs the rest of nodes stats (ex. nodes count)
    3. Pie charts (ex. capacity distribution)
    4. Average stats charts (ex. average channel size)
    5. Stacked area chart of nodes capacities

    - Enter the number of your election:\n\t
    """

    choice = input(msg)

    while check_invalid_choice(choice):
        print("Invalid choice\n")
        choice = input(msg)

    return int(choice)


def generate_chosen_chart(
    choice: int,
    network_basic_stats: pd.DataFrame,
    routing_nodes_stats: pd.DataFrame,
    big_nodes_stats: pd.DataFrame,
    start: datetime = None,
    end: datetime = datetime.strptime(
        datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d"
    ),
):
    f = None  # figure to show
    if choice == 1:  # TOTAL STATS CHARTS
        features = ["total_channels", "total_capacity", "total_nodes"]

        for fe in features:
            # Creates figure
            f = plt.figure(figsize=(16, 9))
            # Plot
            plot_net_statistics(f, network_basic_stats, fe, end, start)
            # Save figure
            s, e = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
            f.savefig(
                f"charts/total_stats/network_stats_{s}_to_{e}_{fe}.png",
                facecolor="#033048",
            )

        f = plt.figure(figsize=(16, 9))
        # plot btc vs usd
        plot_btc_vs_usd_cap(
            f,
            network_basic_stats,
            start,
            end,
        )
        s, e = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
        # save
        f.savefig(
            f"charts/total_stats/network_stats_{s}_to_{e}_btc_vs_usd.png",
            facecolor="#033048",
        )

    elif choice == 2:  # ROUTING VS TOTAL CHART
        features = [
            ("routing_nodes", "total_nodes"),
        ]

        for fe in features:
            # Create figure
            f = plt.figure(figsize=(16, 9))
            # Plot
            plot_routing_vs_net_statistics(
                f,
                routing_nodes_stats,
                network_basic_stats,
                fe[0],
                fe[1],
                end,
                start,
            )
            # Save figure to charts folder
            s, e = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
            f.savefig(
                f"charts/routing_vs_net_nodes/routing_nodes_stats_{s}_to_{e}_{fe[1]}.png",
                facecolor="#033048",
            )

    elif choice == 3:  # PIE CHARTS

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
            f"charts/pie_charts/big_nodes_pie_{end}.png",
            facecolor="#033048",
        )

        # Network's capacity distribution pie chart
        # get nodes capacities
        ln_total_cap, rn_total_cap, big_total_cap = get_capacities(
            network_basic_stats,
            routing_nodes_stats,
            big_nodes_stats,
            big_nodes,
            date=end,
        )
        # Create figure
        f = plt.figure(figsize=(16, 9))
        # plot pie chart
        plot_capacities_pie(f, ln_total_cap, rn_total_cap, big_total_cap)
        # Save figure
        f.savefig(
            f"charts/pie_charts/capacity_distribution_{end}.png",
            facecolor="#033048",
        )

        # Nodes categories pie chart
        # get number of nodes of each category
        rn_count, rest_count, big_count = get_nodes_count(
            network_basic_stats, routing_nodes_stats, big_nodes_stats, date=end
        )
        # Create figure
        f = plt.figure(figsize=(16, 9))
        # Plot chart
        plot_nodes_categories(f, rn_count, rest_count, big_count)
        # Save figure
        f.savefig(
            f"charts/pie_charts/share_nodes_pie_{end}.png",
            facecolor="#033048",
        )

    elif choice == 4:  # AVERAGE CHARTS
        # For average node capacity
        f = plt.figure(figsize=(16, 9))
        # Network basic statistics -> network_basic_stats
        plot_net_statistics(
            f,
            network_basic_stats[["date", "avg_node_capacity"]],
            "avg_node_capacity",
            end,
            start,
        )
        s, e = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
        # Save chart
        f.savefig(
            f"charts/average_stats/avg_node_capacity_{s}_to_{e}.png",
            facecolor="#033048",
        )

        # For average channel size
        f = plt.figure(figsize=(16, 9))
        # Network basic stats : network_basic_stats
        # average channel size
        plot_med_statistics(
            f,
            network_basic_stats[
                ["date", "avg_channel_size", "median_channel_size"]
            ],
            "avg_channel_size",
            end,
            start,
        )
        # Save chart
        f.savefig(
            f"charts/average_stats/avg_chan_size_{s}_to_{e}.png",
            facecolor="#033048",
        )

    else:  # STACKED AREA CHART
        # Get big routing nodes accumulated capacity from 28 days
        # ago until recent
        # load big nodes description
        big_nodes = pd.read_csv(
            "data/processed/basic_stats/big_nodes_desc.csv", index_col=0
        )
        big_nodes, _ = clean_big_nodes(big_nodes)
        big_rn_capacities = get_big_routing_nodes_data(big_nodes, start, end)
        # get accumulated capacity of routing nodes, big nodes and the rest
        x, y_1, y_2, y_3 = get_nodes_capacities(
            network_basic_stats,
            routing_nodes_stats,
            big_nodes_stats.set_index("date", drop=False),
            start,
            end,
            big_rn_capacities,
        )
        # Create figure
        f = plt.figure(figsize=(16, 9))
        # Plot area chart
        plot_area_capacities_chart(f, x, y_1, y_2, y_3)

        s, e = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

        f.savefig(
            f"charts/area_charts/stacked_area_chart_{s}_to_{e}.png",
            facecolor="#033048",
        )


def main():

    # set of the possible args when executing file via command line
    main_args = {
        "--generate_charts",
        "--update",
        "--help",
    }

    received_args = list(sys.argv)
    s_args = set(received_args)  # set of args passed when executing file via cl

    main_args = main_args.intersection(s_args)

    if len(s_args) == 1:  # no args passed
        print("The program needs arguments.")
        sys.exit(0)  # end execution

    if len(main_args) == 0:  # incorrect args passed
        print("Incorrect arguments.")
        sys.exit(0)  # end execution

    # print("WELCOME")
    # time.sleep(3)
    todays_date = None
    net_stats_filename = "data/processed/basic_stats/network_basic_stats.csv"
    routing_stats_file = "data/processed/basic_stats/routing_nodes_stats.csv"
    big_stats_file = "data/processed/basic_stats/big_nodes_stats.csv"
    routing_nodes_stats = None
    network_basic_stats = None
    big_nodes_stats = None

    if "--update" in main_args:
        print("Converting today's network graph into a csv file ...")
        # MISSING CODE
        directory = "data/processed/graphs/"
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

        print(f"Done! Find the new network graph file in:\n\t{directory}")
        time.sleep(3)

        ### NETWORK basic stats
        # Load basic stats csv
        network_basic_stats = load_network_basic_stats(net_stats_filename)
        # Save new basic stats
        add_new_network_stats(network_basic_stats, todays_date)

        #### Stats of ROUTING NODES
        # network's csv graph file
        net_csv = "data/processed/graphs/network_graph_" + todays_date + ".csv"
        # routing nodes stats csv file
        # Save new routing nodes stats
        save_routing_nodes_stats(net_csv, routing_stats_file, todays_date)

        ### BIG NODES stats
        # Save new big nodes stats
        save_big_nodes_stats(net_csv, big_stats_file, todays_date)
        print("Updating network statistics with today's data ...")
        print("Done!")
        time.sleep(3)

    # list of args with one leading "-"
    chart_args = [a for a in received_args if a[0] == "-" and a[1] != "-"]
    dates = [None] * 2  # Empty list
    date_for_pie = None

    if "--generate_charts" in main_args:
        if "-start_date" in chart_args and "-end_date" in chart_args:
            ix_1, ix_2 = received_args.index(
                "-start_date"
            ), received_args.index("-end_date")
            # dates should be provided after start_date and end_date args
            dates[0], dates[1] = (
                received_args[ix_1 + 1],
                received_args[ix_2 + 1],
            )
            for i, d in enumerate(dates):
                if check_invalid_date(d):
                    print(f"{d} is an invalid date.")
                    sys.exit(0)  # end execution
                dates[i] = get_time(d)

        elif "-unique_date" in chart_args:
            ix = received_args.index("-unique_date")
            date_for_pie = received_args[ix + 1]
            if check_invalid_date(date_for_pie):
                print(f"{date_for_pie} is an invalid date.")
                sys.exit(0)  # end execution
            date_for_pie = get_time(date_for_pie)

        else:
            print(
                """When invoquing --generate_charts you have to specify 
                the date or dates of your charts"""
            )
            sys.exit(0)  # end execution

        network_basic_stats = load_network_basic_stats(net_stats_filename)
        routing_nodes_stats = load_routing_nodes_stats(routing_stats_file)
        big_nodes_stats = load_big_nodes_stats(big_stats_file)

        # Cast date column of our dataframes from str to date time
        network_basic_stats = cast_df_date(network_basic_stats)
        routing_nodes_stats = cast_df_date(routing_nodes_stats)
        big_nodes_stats = cast_df_date(big_nodes_stats)

        routing_nodes_stats = routing_nodes_stats.set_index("date", drop=False)
        network_basic_stats = network_basic_stats.set_index("date", drop=False)
        big_nodes_stats = big_nodes_stats.set_index("date", drop=False)

    dates_args = {
        "-start_date",
        "-end_date",
        "unique_date",
    }

    chart_args = set(chart_args) - dates_args
    possible_charts = {
        "-area": 5,
        "-total": 1,
        "-average": 4,
        "-pie": 3,
        "-routing": 2,
    }

    for chart in chart_args:
        generate_chosen_chart(
            possible_charts[chart],
            network_basic_stats,
            routing_nodes_stats,
            big_nodes_stats,
            dates[0],
            dates[1],
        )

    print("\n\tDone! :)")
    # menu = """
    # Now, choose whether to generate charts:
    # 1. Generate charts
    # 2. Don't, end execution.\n\t
    # """
    # # Ask for option
    # opt = input(menu)

    # while True:
    #     generated = False
    #     while check_invalid_choice(opt, menu=True):
    #         print("Invalid option, try again")
    #         opt = input(menu)

    #     if int(opt) == 2:
    #         print("ENDING EXECUTION")
    #         time.sleep(3)
    #         sys.exit(0)

    #     print("Alright\n")
    #     # CHOSE A CHART
    #     chosen_chart = ask_for_chart()
    #     # if chosen chart is pie chart, then only one date needed
    #     if chosen_chart == 3:
    #         date_for_pie = ask_for_date()  # Ask only for one date
    #         # dates[1] = date_for_pie
    #         generate_chosen_chart(
    #             chosen_chart,
    #             network_basic_stats,
    #             routing_nodes_stats,
    #             big_nodes_stats,
    #             end=date_for_pie,
    #         )
    #         generated = True
    #     # CHOOSE DATES
    #     if dates.count(None) == 2 and chosen_chart != 3:  # if dates is empty
    #         start, end = ask_for_pair_of_dates()

    #         while not validate_pair_of_dates(start, end):
    #             print("\nDates difference should be at least of 7 days\n")
    #             start, end = ask_for_pair_of_dates()

    #         dates[0] = start
    #         dates[1] = end

    #     elif chosen_chart != 3:  # already asked for dates before
    #         print("Do you want to enter new dates?")
    #         msg_2 = """
    #         1. Yes
    #         2. No\n\t
    #         """
    #         ans = input(msg_2)
    #         while check_invalid_choice(ans, menu=True):
    #             print("Invalid option, try again")
    #             ans = input(msg_2)
    #         if int(ans) == 1:
    #             start, end = ask_for_pair_of_dates()

    #             while not validate_pair_of_dates(start, end):
    #                 print("\nDates difference should be at least of 7 days\n")
    #                 start, end = ask_for_pair_of_dates()

    #             dates[0] = start
    #             dates[1] = end

    #     if not generated:
    #         print(dates)
    #         generate_chosen_chart(
    #             chosen_chart,
    #             network_basic_stats,
    #             routing_nodes_stats,
    #             big_nodes_stats,
    #             dates[0],
    #             dates[1],
    #         )

    #     print("\nCharts generated successfuly!\n")
    #     time.sleep(2)

    #     opt = input(menu)


if __name__ == "__main__":
    main()
