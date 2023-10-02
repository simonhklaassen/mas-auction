import os
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.lines as mlines
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

def create_graphs(current_directory):

    # Setup
    subdirectories = [d for d in os.listdir(current_directory) if os.path.isdir(d)]

    avg_correction_term_normal_bidders_dict = {}
    avg_correction_term_malicious_bidder_dict = {}
    optimality_dict = {}
    efficiency_dict = {}
    malicious_dict = {}

    x_coordinates_pareto_frontier_dict = {}
    y_coordinates_pareto_frontier_dict = {}

    x_coordinates_pareto_frontier_normal_dict = {}
    x_coordinates_pareto_frontier_malicious_dict = {}
    y_coordinates_pareto_frontier_normal_dict = {}
    y_coordinates_pareto_frontier_malicious_dict = {}

    std_avg_correction_term_normal_bidders_dict = {}
    std_avg_correction_term_malicious_bidder_dict = {}
    std_optimality_dict = {}
    std_efficiency_dict = {}
    std_malicious_dict = {}

    competing_malicious_agents = False
    # numbers_after_decimal_point = 3

    # Extract all experiment results and store them in the respective dictionaries
    for subdirectory in subdirectories:

        total_amount_of_bidders = re.search(r'n=(\d+)', subdirectory)
        if total_amount_of_bidders:
            total_amount_of_bidders = int(total_amount_of_bidders.group(1))

        amount_of_bidders = re.search(r'b=(\d+)', subdirectory)
        if amount_of_bidders:
            amount_of_bidders = int(amount_of_bidders.group(1))

        percentage_of_malicious_agents = int(round(((1 - (amount_of_bidders / total_amount_of_bidders)) * 100), 1))
        percentage_of_malicious_agents = str(percentage_of_malicious_agents) + "%"

        subdirectory_path = os.path.join(current_directory, subdirectory)
        json_files = [f for f in os.listdir(subdirectory_path) if f.endswith('.json')]

        if len(json_files) == 1:
            json_file_path = os.path.join(subdirectory_path, json_files[0])

            with open(json_file_path, 'r') as json_file:
                    result_data = json.load(json_file)

                    for metric in result_data:
                        
                        if metric["metric"] == "avg_correction_term_normal_bidders":
                            avg_correction_term_normal_bidders_dict[percentage_of_malicious_agents] = metric["mean"]
                            std_avg_correction_term_normal_bidders_dict[percentage_of_malicious_agents] = metric["std"]
                    
                        if metric["metric"] == "optimality":
                            optimality_dict[percentage_of_malicious_agents] = metric["mean"]
                            std_optimality_dict[percentage_of_malicious_agents] = metric["std"]

                        if metric["metric"] == "efficiency":
                            efficiency_dict[percentage_of_malicious_agents] = metric["mean"]
                            std_efficiency_dict[percentage_of_malicious_agents] = metric["std"]

                        if metric["metric"] == "avg_correction_term_malicious_bidder":
                            competing_malicious_agents = True
                            avg_correction_term_malicious_bidder_dict[percentage_of_malicious_agents] = metric["mean"]
                            std_avg_correction_term_malicious_bidder_dict[percentage_of_malicious_agents] = metric["std"]
                        
                        if metric["metric"] == "malicious":
                            malicious_dict[percentage_of_malicious_agents] = metric["mean"]
                            std_malicious_dict[percentage_of_malicious_agents] = metric["std"]

                        if metric["metric"] == "x_coordinate_pareto_frontier":
                            x_coordinates_pareto_frontier_dict[percentage_of_malicious_agents] = metric["mean"]

                        if metric["metric"] == "y_coordinate_pareto_frontier":
                            y_coordinates_pareto_frontier_dict[percentage_of_malicious_agents] = metric["mean"]

                        if metric["metric"] == "x_coordinate_pareto_frontier_normal":
                            x_coordinates_pareto_frontier_normal_dict[percentage_of_malicious_agents] = metric["mean"]

                        if metric["metric"] == "x_coordinate_pareto_frontier_malicious":
                            x_coordinates_pareto_frontier_malicious_dict[percentage_of_malicious_agents] = metric["mean"]

                        if metric["metric"] == "y_coordinate_pareto_frontier_normal":
                            y_coordinates_pareto_frontier_normal_dict[percentage_of_malicious_agents] = metric["mean"]
                        
                        if metric["metric"] == "y_coordinate_pareto_frontier_malicious":
                            y_coordinates_pareto_frontier_malicious_dict[percentage_of_malicious_agents] = metric["mean"]

    # Also gather data from the respective baseline case
    dir_baseline = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
    dir_baseline = dir_baseline + "/baseline/n=" + str(total_amount_of_bidders) + "/n=" + str(total_amount_of_bidders) + "|b=" + str(total_amount_of_bidders) + "|sm=0|cm=0/"
    percentage_of_malicious_agents = "0%"

    files = os.listdir(dir_baseline)

    for file in files:
        if file.endswith('.json'):
            json_file = file
            break

    if json_file:
        json_file_path = os.path.join(dir_baseline, json_file)
        with open(json_file_path, 'r') as json_file:
                result_data = json.load(json_file)

                for metric in result_data:
                    
                    if metric["metric"] == "avg_correction_term_normal_bidders":
                        avg_correction_term_normal_bidders_dict[percentage_of_malicious_agents] = metric["mean"]
                        std_avg_correction_term_normal_bidders_dict[percentage_of_malicious_agents] = metric["std"]
                
                    if metric["metric"] == "optimality":
                        optimality_dict[percentage_of_malicious_agents] = metric["mean"]
                        std_optimality_dict[percentage_of_malicious_agents] = metric["std"]

                    if metric["metric"] == "efficiency":
                        efficiency_dict[percentage_of_malicious_agents] = metric["mean"]
                        std_efficiency_dict[percentage_of_malicious_agents] = metric["std"]

                    if metric["metric"] == "x_coordinate_pareto_frontier":
                        x_coordinates_pareto_frontier_dict[percentage_of_malicious_agents] = metric["mean"]
                        if competing_malicious_agents == True:
                            x_coordinates_pareto_frontier_normal_dict[percentage_of_malicious_agents] = metric["mean"]

                    if metric["metric"] == "y_coordinate_pareto_frontier":
                        y_coordinates_pareto_frontier_dict[percentage_of_malicious_agents] = metric["mean"]
                        if competing_malicious_agents == True:
                            y_coordinates_pareto_frontier_normal_dict[percentage_of_malicious_agents] = metric["mean"]
    else:
        print("No JSON file found in the current directory.")

    # Transform dictionaries into Pandas series
    avg_correction_term_normal_bidders = pd.Series(avg_correction_term_normal_bidders_dict)
    optimality = pd.Series(optimality_dict)
    efficiency = pd.Series(efficiency_dict)
    if competing_malicious_agents == True:
        avg_correction_term_malicious_bidder = pd.Series(avg_correction_term_malicious_bidder_dict)
        malicious = pd.Series(malicious_dict)

        x_coordinates_pareto_frontier_normal = pd.Series(x_coordinates_pareto_frontier_normal_dict)
        x_coordinates_pareto_frontier_malicious = pd.Series(x_coordinates_pareto_frontier_malicious_dict)
        y_coordinates_pareto_frontier_normal = pd.Series(y_coordinates_pareto_frontier_normal_dict)
        y_coordinates_pareto_frontier_malicious = pd.Series(y_coordinates_pareto_frontier_malicious_dict)

        x_coordinates_pareto_frontier_normal = x_coordinates_pareto_frontier_normal.sort_index()
        x_coordinates_pareto_frontier_malicious = x_coordinates_pareto_frontier_malicious.sort_index()
        y_coordinates_pareto_frontier_normal = y_coordinates_pareto_frontier_normal.sort_index()
        y_coordinates_pareto_frontier_malicious = y_coordinates_pareto_frontier_malicious.sort_index()

    if x_coordinates_pareto_frontier_dict:
        x_coordinates_pareto_frontier = pd.Series(x_coordinates_pareto_frontier_dict)
    if y_coordinates_pareto_frontier_dict:
        y_coordinates_pareto_frontier = pd.Series(y_coordinates_pareto_frontier_dict)

    std_avg_correction_term_normal_bidders = pd.Series(std_avg_correction_term_normal_bidders_dict)
    std_optimality = pd.Series(std_optimality_dict)
    std_efficiency = pd.Series(std_efficiency_dict)
    if competing_malicious_agents == True:
        std_malicious = pd.Series(std_malicious_dict)
        std_avg_correction_term_malicious_bidder = pd.Series(std_avg_correction_term_malicious_bidder_dict)

    # Bar Graph 
    # Reorganize data so that it can be transformed into a DataFrame
    if competing_malicious_agents == True:
        data = {
                'Percentage of Wins by Malicious Bidders': malicious,
                'Average Correction Term of the Malicious Bidder': avg_correction_term_malicious_bidder,
                'Average Correction Term of Normal Bidders': avg_correction_term_normal_bidders,
                'Efficiency': efficiency,
                'Optimality': optimality
                }

        data_std = {
                'Percentage of Wins by Malicious Bidders': std_malicious,
                'Average Correction Term of the Malicious Bidder': std_avg_correction_term_malicious_bidder,
                'Average Correction Term of Normal Bidders': std_avg_correction_term_normal_bidders,
                'Efficiency': std_efficiency,
                'Optimality': std_optimality
                }
    else:
        data = {
                'Average Correction Term of Normal Bidders': avg_correction_term_normal_bidders,
                'Efficiency': efficiency,
                'Optimality': optimality
                }

        data_std = {
                'Average Correction Term of Normal Bidders': std_avg_correction_term_normal_bidders,
                'Efficiency': std_efficiency,
                'Optimality': std_optimality
                }

    df = pd.DataFrame(data)
    df = df.sort_index(ascending=False)
    df_std = pd.DataFrame(data_std)

    # Create the graph
    fig, ax = plt.subplots(figsize=(12, 6))

    # Create the bars
    if competing_malicious_agents == True:
        bar_plot = df.plot(kind='barh', ax=ax, capsize=4, alpha=0.7, color=['Red', 'Black', 'Gray', 'Green', 'MediumBlue'], width=0.8) 
    else:
        bar_plot = df.plot(kind='barh', ax=ax, capsize=4, alpha=0.7, color=['Gray', 'Green', 'MediumBlue'], width=0.8) 

    # Some design adjustments
    ax.set_xlim(0,1)
    plt.title('Comparison of Average Auction Outcomes, depending on the Amount of Spiteful Bidders')
    plt.ylabel('Percentage of malicious Agents')
    extra_ticks = [i / 10 for i in range(11)]
    plt.xticks(list(plt.xticks()[0]) + extra_ticks)

    # Specify the order of legend labels and create the legend
    if competing_malicious_agents == True:
        desired_legend_order = ['Optimality',
        'Efficiency',
        'Average Correction Term of Normal Bidders',
        'Average Correction Term of the Malicious Bidder',
        'Percentage of Wins by Malicious Bidders']
    else:
        desired_legend_order = ['Optimality',
        'Efficiency',
        'Average Correction Term of Normal Bidders']

    handles, labels = ax.get_legend_handles_labels()
    label_to_handle = dict(zip(labels, handles))
    ordered_handles = [label_to_handle[label] for label in desired_legend_order]
    ordered_labels = desired_legend_order
    ax.legend(ordered_handles, ordered_labels, loc='upper right')

    # Annotate the bars
    for i, (values, std_values) in enumerate(zip(df.values, df_std.values)):
        z=0
        for v, std in zip(values, std_values):
            x_coord = v + 0.01
            if competing_malicious_agents == True:
                y_coord = i - 0.335
            else:
                y_coord = i - 0.27
            if competing_malicious_agents == True:
                sp = 0.16
            else:
                sp = 0.16 * (5/3)
            bar_plot.annotate(f'{v:.2f}', xy=(x_coord, y_coord + sp * z), va='center', color='gray', fontsize=7, fontweight='bold')
            z += 1

    experiment_name = "bar_graph_" + current_directory.split("/")[-1]
    plt.savefig(experiment_name + ".png", dpi=200)

    # Pareto Front
    # Fonts for the graph
    font_title = {
        'family': 'Palatino',
        'weight': 'bold',
        'size': 15
    }

    font_rest = {
        'family': 'Palatino',
        'weight': 'normal',
        'size': 10
    }

    font_zoom = {
        'family': 'Palatino',
        'weight': 'normal',
        'size': 11
    }

    font_axis = {
        'family': 'Palatino',
        'weight': 'normal',
        'size': 12.5
    }

    # Create the graph
    plt.figure(figsize=(6, 6))

    # Determine the range of the x and y-axis
    min_x = x_coordinates_pareto_frontier.min()
    max_x = x_coordinates_pareto_frontier.max()
    min_y = y_coordinates_pareto_frontier.min()
    max_y = y_coordinates_pareto_frontier.max()
    extra = 0.07

    rect_x_min = min_x - extra
    rect_y_min = min_y - extra
    rect_width = max_x - min_x + 2 * extra
    rect_height = max_y - min_y + 2 * extra

    plt.xlim(min_x - extra, max_x + extra)
    plt.ylim(min_y - extra, max_y + extra)

    plt.xticks(fontname='Palatino', fontsize=10.5)
    plt.yticks(fontname='Palatino', fontsize=10.5)

    # Plot the average auction outcomes
    x_coordinates_pareto_frontier = x_coordinates_pareto_frontier.sort_index()
    y_coordinates_pareto_frontier = y_coordinates_pareto_frontier.sort_index()
    colors = ['Green', 'Blue', 'Purple', '#FFD700', 'Orange', 'Red']
    if competing_malicious_agents == True:
        plt.scatter(x_coordinates_pareto_frontier_normal, y_coordinates_pareto_frontier_normal, label='Data Points', color=colors, edgecolor='Black', marker='o', s=25, zorder=3)
        plt.scatter(x_coordinates_pareto_frontier_malicious, y_coordinates_pareto_frontier_malicious, label='Data Points', color=colors[1:], edgecolor='Black', marker='D', s=25, zorder=3)
    else:
        plt.scatter(x_coordinates_pareto_frontier, y_coordinates_pareto_frontier, label='Data Points', color=colors, edgecolor='Black', marker='o', s=25, zorder=3)

    # Create the Pareto front and the x and y axis
    plt.plot([1.1, -0.1], [-0.1, 1.1], color='Gray', linestyle='--', linewidth=1, label='Pareto Front', zorder=2)
    plt.axhline(0, color='black', linewidth=0.5, zorder=1)  
    plt.axvline(0, color='black', linewidth=0.5, zorder=1) 

    # Set plot labels and title
    plt.xlabel('Utility of the Winning Bidder', fontdict=font_axis)
    plt.ylabel('Utility of the Auctioneer', fontdict=font_axis)
    plt.title("Average Auction Outcomes per\nExperimental Setting Relative to the Pareto Front", 
                fontdict=font_title, pad=13
    )

    # Create the legend
    type_of_experiment = ""
    for i in ['malicious-collaborative', 'malicious-solo']:
        if i in current_directory:
            if i == 'malicious-collaborative':
                name = 'CSB'
            if i == 'malicious-solo':
                name = 'ISB'
            type_of_experiment = name
            break
    if type_of_experiment == "":
        type_of_experiment = "Basline"
        name = 'Baseline'

    if type_of_experiment == "Baseline":
        label_experiment_type = "Experiment: \n" + type_of_experiment
    else: 
        label_experiment_type = "Experiment: " + type_of_experiment
    label_n = "n = " + str(total_amount_of_bidders)

    if type_of_experiment == "CSB":

        legend_handles = [
            mlines.Line2D([], [], marker='.', color='Black', markeredgecolor='black', markeredgewidth=1, linestyle='None', label=label_experiment_type),
            mlines.Line2D([], [], marker='.', color='Black', markeredgecolor='black', markeredgewidth=1, linestyle='None', label=label_n),
            mlines.Line2D([], [], marker='D', color='White', markeredgecolor='black', markeredgewidth=1, linestyle='None', label="Spiteful Winner"),
            mlines.Line2D([], [], marker='o', color='White', markeredgecolor='black', markeredgewidth=1, linestyle='None', label="Non-Spiteful Winner"),
            mlines.Line2D([], [], marker='s', color='Green', markersize=8, label='0% Spiteful Bidders', linestyle='None'),
            mlines.Line2D([], [], marker='s', color='Blue', markersize=8, label='10% Spiteful Bidders', linestyle='None'),
            mlines.Line2D([], [], marker='s', color='Purple', markersize=8, label='20% Spiteful Bidders', linestyle='None'),
            mlines.Line2D([], [], marker='s', color='#FFD700', markersize=8, label='30% Spiteful Bidders', linestyle='None'),
            mlines.Line2D([], [], marker='s', color='Orange', markersize=8, label='40% Spiteful Bidders', linestyle='None'),
            mlines.Line2D([], [], marker='s', color='Red', markersize=8, label='50% Spiteful Bidders', linestyle='None'),
            mlines.Line2D([], [], color='Gray', linestyle='--', label='Pareto Front')
        ]

    elif type_of_experiment == "ISB": 

        legend_handles = [
            mlines.Line2D([], [], marker='.', color='Black', markeredgecolor='black', markeredgewidth=1, linestyle='None', label=label_experiment_type),
            mlines.Line2D([], [], marker='.', color='Black', markeredgecolor='black', markeredgewidth=1, linestyle='None', label=label_n),
            mlines.Line2D([], [], marker='o', color='Green', markeredgecolor='black', markeredgewidth=1,markersize=8, label='0% Spiteful Bidders', linestyle='None'),
            mlines.Line2D([], [], marker='o', color='Blue', markeredgecolor='black', markeredgewidth=1,markersize=8, label='10% Spiteful Bidders', linestyle='None'),
            mlines.Line2D([], [], marker='o', color='Purple', markeredgecolor='black', markeredgewidth=1,markersize=8, label='20% Spiteful Bidders', linestyle='None'),
            mlines.Line2D([], [], marker='o', color='#FFD700', markeredgecolor='black', markeredgewidth=1,markersize=8, label='30% Spiteful Bidders', linestyle='None'),
            mlines.Line2D([], [], marker='o', color='Orange', markeredgecolor='black', markeredgewidth=1,markersize=8, label='40% Spiteful Bidders', linestyle='None'),
            mlines.Line2D([], [], marker='o', color='Red', markeredgecolor='black', markeredgewidth=1,markersize=8, label='50% Spiteful Bidders', linestyle='None'),
            mlines.Line2D([], [], color='Gray', linestyle='--', label='Pareto Front')
        ]
    
    else:

        legend_handles = [
            mlines.Line2D([], [], marker='>', color='White', markeredgecolor='black', markeredgewidth=1, linestyle='None', label=label_experiment_type),
            mlines.Line2D([], [], marker='>', color='White', markeredgecolor='black', markeredgewidth=1, linestyle='None', label=label_n),
            mlines.Line2D([], [], marker='o', color='Green', markersize=8, label='Final Allocations', markeredgecolor='black', markeredgewidth=1, linestyle='None'),
            mlines.Line2D([], [], color='Gray', linestyle='--', label='Pareto Front')
        ]

    plt.legend(handles=legend_handles, prop=font_rest, loc="upper right")

    # Create the Zoom-Out
    axins = inset_axes(plt.gca(), width="35%", height="35%", loc="lower left")

    rect = plt.Rectangle((rect_x_min, rect_y_min), rect_width, rect_height,
                        linewidth=1, edgecolor='Black', facecolor='none', linestyle='-')
    plt.gca().add_patch(rect)

    if competing_malicious_agents == True:
        axins.scatter(x_coordinates_pareto_frontier_normal, y_coordinates_pareto_frontier_normal, label='Data Points', color=colors, edgecolor='Black', marker='o', s=25, zorder=3)
        axins.scatter(x_coordinates_pareto_frontier_malicious, y_coordinates_pareto_frontier_malicious, label='Data Points', color=colors[1:], edgecolor='Black', marker='D', s=25, zorder=3)
    else:
        axins.scatter(x_coordinates_pareto_frontier, y_coordinates_pareto_frontier, label='Data Points', color=colors, edgecolor='Black', marker='o', s=25, zorder=3)
    axins.plot([1.1, -0.1], [-0.1, 1.1], color='Gray', linestyle='--', label='Pareto Front',zorder=2)
    axins.axhline(0, color='black', linewidth=0.5, zorder=1)  
    axins.axvline(0, color='black', linewidth=0.5, zorder=1)  

    # Some design Adjustments
    axins.spines['left'].set_linewidth(1.5)  
    axins.spines['bottom'].set_linewidth(1.5)  
    axins.spines['right'].set_linewidth(1.5)  
    axins.spines['top'].set_linewidth(1.5)  

    axins.set_xlim(-0.1,1.1)
    axins.set_ylim(-0.1,1.1)
    axins.set_xticks([])
    axins.set_yticks([])
    axins.set_title('Zoom-Out',                 
                    fontdict=font_zoom
    )

    # Save the image in the current directory
    experiment_name = "pareto_frontier_" + current_directory.split("/")[-1]
    plt.savefig(experiment_name + ".png", dpi=200)


