from __future__ import print_function
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

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
import os.path
import io


def download_file(service, real_file_id, local_fd):
    """Downloads a file
    Args:
        service: Drive API Service instance.
        real_file_id: ID of the file to download
        local_fd: io.Base or file object, the stream that the Drive file's
            contents will be written to.
    """

    try:
        file_id = real_file_id

        # pylint: disable=maybe-no-member
        request = service.files().get_media(fileId=file_id)
        # file = io.BytesIO()
        downloader = MediaIoBaseDownload(local_fd, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}.")

    except HttpError as error:
        print(f"An error occurred: {error}")

    return


def get_files(service, real_folder_id, team_id):
    """Gets files (names, ids) of specific folder
    Args:
        service: Drive API Service instance.
        real_folder_id: ID of the folder to query
        team_id: Team's Drive ID
    Returns:
        List of files
    """

    try:
        folder_id = real_folder_id
        # Use the service object to get a list of files in the specified folder
        team_drive_id = team_id

        # Use the service object to get a list of files in the specified folder in the Team Drive
        results = (
            service.files()
            .list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="files(id, name)",
                corpora="drive",
                driveId=team_drive_id,
                includeItemsFromAllDrives="true",
                supportsAllDrives="true",
                pageSize=1000,
            )
            .execute()
        )
        items = results.get("files", [])

        return items

    except HttpError as error:
        print(f"An error occurred: {error}")


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
    ln_graph=None,
    desc_file=None,
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
                f"../charts/total_stats/network_stats_{s}_to_{e}_{fe}.png",
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
            f"../charts/total_stats/network_stats_{s}_to_{e}_btc_vs_usd.png",
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
                f"../charts/routing_vs_net_nodes/routing_nodes_stats_{s}_to_{e}_{fe[1]}.png",
                facecolor="#033048",
            )

    elif choice == 3:  # PIE CHARTS
        e = end.strftime("%Y-%m-%d")
        # Big nodes categories distribution pie chart
        # Update industrial nodes individual capacities
        big_nodes = pd.read_csv(desc_file, index_col=0)
        # industrial nodes pub keys
        industrial_keys = big_nodes.loc[:, "pub_key"].values
        # Get those nodes capacities
        industrial_caps = ln_graph[ln_graph["pub_key"].isin(industrial_keys)][
            ["pub_key", "alias", "total_capacity"]
        ]
        # update capacities
        big_nodes["total_capacity"] = industrial_caps["total_capacity"].values
        print(big_nodes[["alias", "total_capacity"]])
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
            f"../charts/pie_charts/big_nodes_pie_{e}.png",
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
            f"../charts/pie_charts/capacity_distribution_{e}.png",
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
            f"../charts/pie_charts/share_nodes_pie_{e}.png",
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
            f"../charts/average_stats/avg_node_capacity_{s}_to_{e}.png",
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
            f"../charts/average_stats/avg_chan_size_{s}_to_{e}.png",
            facecolor="#033048",
        )

    else:  # STACKED AREA CHART
        # Get big routing nodes accumulated capacity from 28 days
        # ago until recent
        # load big nodes description
        big_nodes = pd.read_csv(
            "../data/processed/basic_stats/big_nodes_desc.csv", index_col=0
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
            f"../charts/area_charts/stacked_area_chart_{s}_to_{e}.png",
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
    net_stats_filename = "../data/processed/basic_stats/network_basic_stats.csv"
    routing_stats_file = "../data/processed/basic_stats/routing_nodes_stats.csv"
    big_stats_file = "../data/processed/basic_stats/big_nodes_stats.csv"
    big_nodes_desc_file = "../data/processed/basic_stats/big_nodes_desc.csv"
    routing_nodes_stats = None
    network_basic_stats = None
    big_nodes_stats = None

    if "--update" in main_args:

        # If modifying these scopes, delete the file token.json.
        SCOPES = ["https://www.googleapis.com/auth/drive"]

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        try:
            service = build("drive", "v3", credentials=creds)

        except HttpError as error:
            # TODO(developer) - Handle errors from drive API.
            print(f"An error occurred: {error}")

        # Open drive_ids.txt file in read-only mode
        with open("drive_ids.txt", "r") as f:
            # Read all the lines of the file into a list
            lines = f.readlines()
        # First line holds the folder id
        folder_id = lines[0][lines[0].find(":") + 2 :].rstrip()
        # Second line holds the team's drive id
        team_id = lines[1][lines[1].find(":") + 2 :].rstrip()
        # Get a list of the files in our graph metrics Shared Drive folder
        graph_files = get_files(service, folder_id, team_id)

        # Get today's date in format <year-month-day>
        todays_date = datetime.now().strftime("%Y-%m-%d")
        # todays_date = "2022-12-29"  ### THIS IS JUST FOR TESTING

        curr_file_name = None
        for file in graph_files:
            if f"graph_metrics_{todays_date}" in file["name"]:
                curr_file_name = file["name"]  # save today's file name
                break
        curr_file_id = None
        for file in graph_files:
            file_name = file["name"]
            if file_name == curr_file_name:
                curr_file_id = file["id"]  # Found today's file id
                break

        filename = "../data/raw/graph_metrics_" + todays_date + ".json.tar.gz"
        # stream that the drive's file content will be written to
        fh = io.FileIO(filename, "wb")
        # downloads current's date graph metrics .json file and saves it
        download_file(service, curr_file_id, fh)

        print("\nSUCCESSFUL DOWNLOAD")

        print("\nConverting today's network graph into a csv file ...")
        filename = "../data/raw/graph_metrics_" + todays_date + ".json.tar.gz"
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
        dir = "../data/processed/graphs"
        ln_graph.to_csv(f"{dir}/network_graph_{todays_date}.csv")

        print(f"Done! Find the new network graph file in:\n\t{dir}")
        time.sleep(3)

        ### NETWORK basic stats
        print("Updating network statistics with today's data ...")
        # Load basic stats csv
        network_basic_stats = load_network_basic_stats(net_stats_filename)
        # Save new basic stats
        add_new_network_stats(network_basic_stats, todays_date)

        #### Stats of ROUTING NODES
        # network's csv graph file
        net_csv = (
            "../data/processed/graphs/network_graph_" + todays_date + ".csv"
        )
        # routing nodes stats csv file
        # Save new routing nodes stats
        save_routing_nodes_stats(net_csv, routing_stats_file, todays_date)

        ### BIG NODES stats
        # Save new big nodes stats
        save_big_nodes_stats(
            net_csv, big_stats_file, big_nodes_desc_file, todays_date
        )

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
        "-unique_date",
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
        if chart != "-pie":
            generate_chosen_chart(
                possible_charts[chart],
                network_basic_stats,
                routing_nodes_stats,
                big_nodes_stats,
                dates[0],
                dates[1],
            )
        else:
            date = date_for_pie.strftime("%Y-%m-%d")
            ln_graph = pd.read_csv(
                f"../data/processed/graphs/network_graph_{date}.csv"
            )
            generate_chosen_chart(
                possible_charts[chart],
                network_basic_stats,
                routing_nodes_stats,
                big_nodes_stats,
                end=date_for_pie,
                ln_graph=ln_graph,
                desc_file=big_nodes_desc_file,
            )

    print("\n\tEnding Execution...")


if __name__ == "__main__":
    main()
