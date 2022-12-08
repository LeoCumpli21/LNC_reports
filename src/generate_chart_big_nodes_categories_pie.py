from generate_charts import *


def clean_big_nodes(df):
    """
    df: big nodes description dataframe

    returns (cleaned df, industrial nodes df without ruting nodes)
    """

    df.drop(columns='Comment', axis=1, inplace=True)
    df['type'] = df['type'].apply(lambda x: ' '.join([w.capitalize() for w in x.split()]))
    df['type'] = df['type'].apply(lambda x: "Ln Wallet" if x == "Wallet" else x)
    # Get rid of category: "Routing Nodes"
    industrial_nodes = df[df['type'] != "Routing Node"]

    return df, industrial_nodes

def get_big_nodes_distribution(df):
    """
    df: industrial nodes dataframe. These exclude routing nodes

    returns a list of (key, value) tupples
    """

    big_nodes_distr = df.type.to_dict()
    d_values = list(big_nodes_distr.values())
    d = {k: d_values.count(k) for k in d_values} 
    # d has the form {'node category': occurrences}
    key_value = d.items()

    return list(key_value)

def plot_big_nodes_distribution(f, dist_list):
    """
    Plots the big nodes distribution pie chart

    f: matplotplib figure
    dist_list: list of (key, value) tupples represnting
        the distribution of big node categories

    returns None
    """

    # f = plt.figure(figsize=(16,9))
    rc = {
        'axes.grid' : True, # for horizontal lines for each y-axis point
        'grid.color': '#436280',
        'font.size': 20,
    }
    plt.rcParams.update(rc)

    # Set figure background to be transparent
    f.patch.set_alpha(0)
    ax = f.add_subplot(111)
    ax.patch.set_alpha(0)
    # Plotting the pie
    _, texts, autotexts = plt.pie(
        [v[1] for v in dist_list], 
        labels=[k[0] for k in dist_list],
        colors = ['#5D89B3', '#436280']*2,
        autopct='%1.1f%%'
    );
    # for the text inside the pie
    for i, autotext in enumerate(autotexts):
        if i< 4:
            autotext.set_color('#FFFFFF')
    else:
        autotext.set_color('black')
    # for text of labels
    for text in texts:
        text.set_color('#FFFFFF')

    return

