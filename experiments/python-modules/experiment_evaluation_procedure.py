import os
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

def procedure(path):

    # Setup
    total_amount_of_bidders = re.search(r'n=(\d+)', path)
    if total_amount_of_bidders:
        total_amount_of_bidders = int(total_amount_of_bidders.group(1))

    amount_of_normal_bidders = re.search(r'b=(\d+)', path)
    if amount_of_normal_bidders:
        amount_of_normal_bidders = int(amount_of_normal_bidders.group(1))
    
    percentage_of_malicious_agents = int(round(((1 - (amount_of_normal_bidders / total_amount_of_bidders)) * 100), 1))
    percentage_of_malicious_agents = str(percentage_of_malicious_agents) + "%"

    type_of_experiment = ""
    for i in ['malicious-collaborative', 'malicious-solo']:
        if i in path:
            type_of_experiment = i
            break
    if type_of_experiment == "":
        type_of_experiment = "baseline"

    directory_experiment_results = path + "/result/"

    list_json_files = os.listdir(directory_experiment_results)
    amount_of_json_files = 0

    problem_complexity_dict = {}
    problem_size_dict = {}
    avg_correction_term_normal_bidders_dict = {}
    avg_correction_term_malicious_bidder_dict = {}
    optimality_dict = {}
    efficiency_dict = {}
    malicious_dict = {}
    x_coordinates_pareto_frontier_dict = {}
    y_coordinates_pareto_frontier_dict = {}

    optimality_malicious_winner_dict = {}
    optimality_normal_winner_dict = {}
    efficiency_malicious_winner_dict = {}
    efficiency_normal_winner_dict = {}

    competing_malicious_agents = False
    numbers_after_decimal_point = 3

    # Extract all experiment results and store them in the respective dictionaries
    for filename in list_json_files:

        if filename.endswith('.json'):

            file_path = os.path.join(directory_experiment_results, filename)
            amount_of_json_files += 1

            match = re.search(r'experiment(\d+)\.json', filename)

            if match:
                exp_nr = int(match.group(1))

            with open(file_path, 'r') as json_file:

                result_data = json.load(json_file)
                
                problem_complexity_dict[exp_nr] = result_data["problem_complexity"]
                problem_size_dict[exp_nr] = result_data["problem_size"]
                avg_correction_term_normal_bidders_dict[exp_nr] = result_data["avg_correction_term_normal_bidders"]
                optimality_dict[exp_nr] = result_data["optimality"]
                efficiency_dict[exp_nr] = result_data["efficiency"]
                if "avg_correction_term_malicious_bidder" in result_data:
                    avg_correction_term_malicious_bidder_dict[exp_nr] = result_data["avg_correction_term_malicious_bidder"]
                    competing_malicious_agents = True
                if "malicious" in result_data: 
                    malicious_dict[exp_nr] = result_data["malicious"]
                    if result_data["malicious"] == 1:
                        optimality_malicious_winner_dict[exp_nr] = result_data["optimality"]
                        efficiency_malicious_winner_dict[exp_nr] = result_data["efficiency"]
                    else:
                        optimality_normal_winner_dict[exp_nr] = result_data["optimality"]
                        efficiency_normal_winner_dict[exp_nr] = result_data["efficiency"]
                if "x_coordinate_pareto_frontier" in result_data:
                    x_coordinates_pareto_frontier_dict[exp_nr] = result_data["x_coordinate_pareto_frontier"]
                if "y_coordinate_pareto_frontier" in result_data:
                    y_coordinates_pareto_frontier_dict[exp_nr] = result_data["y_coordinate_pareto_frontier"]

    problem_complexity = pd.Series(problem_complexity_dict)
    problem_size = pd.Series(problem_size_dict)
    avg_correction_term_normal_bidders = pd.Series(avg_correction_term_normal_bidders_dict)
    optimality = pd.Series(optimality_dict)
    efficiency = pd.Series(efficiency_dict)
    if competing_malicious_agents == True:
        avg_correction_term_malicious_bidder = pd.Series(avg_correction_term_malicious_bidder_dict)
        malicious = pd.Series(malicious_dict)
        optimality_malicious_winner = pd.Series(optimality_malicious_winner_dict)
        optimality_normal_winner = pd.Series(optimality_normal_winner_dict)
        efficiency_malicious_winner = pd.Series(efficiency_malicious_winner_dict)
        efficiency_normal_winner = pd.Series(efficiency_normal_winner_dict)
    if x_coordinates_pareto_frontier_dict:
        x_coordinates_pareto_frontier = pd.Series(x_coordinates_pareto_frontier_dict)
        x_coordinates_pareto_frontier = x_coordinates_pareto_frontier.sort_index()
    if y_coordinates_pareto_frontier_dict:
        y_coordinates_pareto_frontier = pd.Series(y_coordinates_pareto_frontier_dict)
        y_coordinates_pareto_frontier = y_coordinates_pareto_frontier.sort_index()

    if competing_malicious_agents == True:

            x_coordinates_pareto_frontier_normal_dict = {}
            y_coordinates_pareto_frontier_normal_dict = {}
            x_coordinates_pareto_frontier_malicious_dict = {}
            y_coordinates_pareto_frontier_malicious_dict = {}

            for i in range(1, len(x_coordinates_pareto_frontier) + 1):
                if malicious[i] == 0:
                    x_coordinates_pareto_frontier_normal_dict[i] = x_coordinates_pareto_frontier[i]
                    y_coordinates_pareto_frontier_normal_dict[i] = y_coordinates_pareto_frontier[i]
                else:
                    x_coordinates_pareto_frontier_malicious_dict[i] = x_coordinates_pareto_frontier[i]
                    y_coordinates_pareto_frontier_malicious_dict[i] = y_coordinates_pareto_frontier[i]


    # Calculate means
    mean_avg_correction_term_normal_bidders = round(avg_correction_term_normal_bidders.mean(), numbers_after_decimal_point)
    mean_optimality = round(optimality.mean(), numbers_after_decimal_point)
    mean_efficiency = round(efficiency.mean(), numbers_after_decimal_point)
    mean_x_coordinates_pareto_frontier = round(x_coordinates_pareto_frontier.mean(), numbers_after_decimal_point)
    mean_y_coordinates_pareto_frontier = round(y_coordinates_pareto_frontier.mean(), numbers_after_decimal_point)

    if competing_malicious_agents:
        mean_malicious = round(malicious.mean(), numbers_after_decimal_point)
        mean_avg_correction_term_malicious_bidder = round(avg_correction_term_malicious_bidder.mean(), numbers_after_decimal_point)
        mean_optimality_malicious_winner = round(optimality_malicious_winner.mean(), numbers_after_decimal_point)
        mean_optimality_normal_winner = round(optimality_normal_winner.mean(), numbers_after_decimal_point)
        mean_efficiency_malicious_winner = round(efficiency_malicious_winner.mean(), numbers_after_decimal_point)
        mean_efficiency_normal_winner = round(efficiency_normal_winner.mean(), numbers_after_decimal_point)
        mean_x_coordinates_pareto_frontier_normal = round(pd.Series(x_coordinates_pareto_frontier_normal_dict).mean(), numbers_after_decimal_point)
        mean_x_coordinates_pareto_frontier_malicious = round(pd.Series(x_coordinates_pareto_frontier_malicious_dict).mean(), numbers_after_decimal_point)
        mean_y_coordinates_pareto_frontier_normal = round(pd.Series(y_coordinates_pareto_frontier_normal_dict).mean(), numbers_after_decimal_point)
        mean_y_coordinates_pareto_frontier_malicious = round(pd.Series(y_coordinates_pareto_frontier_malicious_dict).mean(), numbers_after_decimal_point)

    # Calculate standard deviations
    std_avg_correction_term_normal_bidders = round(avg_correction_term_normal_bidders.std(), numbers_after_decimal_point)
    std_optimality = round(optimality.std(), numbers_after_decimal_point)
    std_efficiency = round(efficiency.std(), numbers_after_decimal_point)
    if competing_malicious_agents == True:
        std_malicious = round(malicious.std(), numbers_after_decimal_point)
        std_avg_correction_term_malicious_bidder = round(avg_correction_term_malicious_bidder.std(), numbers_after_decimal_point)
        std_optimality_malicious_winner = round(optimality_malicious_winner.std(), numbers_after_decimal_point)
        std_optimality_normal_winner = round(optimality_normal_winner.std(), numbers_after_decimal_point)
        std_efficiency_malicious_winner = round(efficiency_malicious_winner.std(), numbers_after_decimal_point)
        std_efficiency_normal_winner = round(efficiency_normal_winner.std(), numbers_after_decimal_point)

    # Calculate how often Underbidding occurs
    amount_of_underbidding = 0
    amount_of_underbidding_normal = 0
    amount_of_underbidding_malicious = 0

    amount_of_experiments = 0
    amount_of_experiments_normal_winner = 0

    amount_of_experiments_malicious_winner = 0
    amount_of_experiments_normal_winner = 0
    if competing_malicious_agents == True:
        for i in range(1, 73):
            if malicious[i] == 1:
                amount_of_experiments_malicious_winner += 1
                if pd.Series(x_coordinates_pareto_frontier_malicious_dict)[i] < 0:
                    amount_of_underbidding_malicious += 1
            else:
                amount_of_experiments_normal_winner += 1
                if pd.Series(x_coordinates_pareto_frontier_normal_dict)[i] < 0:
                    amount_of_underbidding_normal += 1
    else: 
        for i in range(1, len(x_coordinates_pareto_frontier)+1):
            amount_of_experiments += 1
            if x_coordinates_pareto_frontier[i] < 0:
                amount_of_underbidding += 1
    
    if competing_malicious_agents == False:
        percentage_underbidding = round((amount_of_underbidding / amount_of_experiments) * 100, 1)
        # print(f"In {percentage_underbidding}% of the cases, the winning bidder underbids his execution cost.")
    else:
        percentage_underbidding_malicious = round((amount_of_underbidding_malicious / amount_of_experiments_malicious_winner) * 100, 1)
        percentage_underbidding_normal = round((amount_of_underbidding_normal / amount_of_experiments_normal_winner) * 100, 1)
        # print(f"Normal Winner: In {percentage_underbidding_normal}% of the cases, the winning bidder underbids his execution cost.")
        # print(f"Malicious Winner: In {percentage_underbidding_malicious}% of the cases, the winning malicious bidder underbids his execution cost.")


    # Store results in a .json file.
    if competing_malicious_agents == True and x_coordinates_pareto_frontier_dict:
        data = [
            {
                "metric": "avg_correction_term_normal_bidders",
                "mean": mean_avg_correction_term_normal_bidders,
                "std": std_avg_correction_term_normal_bidders
            },
            {
                "metric": "optimality",
                "mean": mean_optimality,
                "std": std_optimality
            },
            {
                "metric": "efficiency",
                "mean": mean_efficiency,
                "std": std_efficiency
            },
            {
                "metric": "avg_correction_term_malicious_bidder",
                "mean": mean_avg_correction_term_malicious_bidder,
                "std": std_avg_correction_term_malicious_bidder
            },
            {
                "metric": "malicious",
                "mean": mean_malicious,
                "std": std_malicious
            },
            {
                "metric": "optimality_normal_winner",
                "mean": mean_optimality_normal_winner,
                "std": std_optimality_normal_winner
            },
            {
                "metric": "optimality_malicious_winner",
                "mean": mean_optimality_malicious_winner,
                "std": std_optimality_malicious_winner
            },
            {
                "metric": "efficiency_normal_winner",
                "mean": mean_efficiency_normal_winner,
                "std": std_efficiency_normal_winner
            },
            {
                "metric": "efficiency_malicious_winner",
                "mean": mean_efficiency_malicious_winner,
                "std": std_efficiency_malicious_winner
            },
            {
                "metric": "x_coordinate_pareto_frontier_normal",
                "mean": mean_x_coordinates_pareto_frontier_normal
            }, 
            {
                "metric": "x_coordinate_pareto_frontier_malicious",
                "mean": mean_x_coordinates_pareto_frontier_malicious
            }, 
            {
                "metric": "y_coordinate_pareto_frontier_normal",
                "mean": mean_y_coordinates_pareto_frontier_normal
            },
            {
                "metric": "y_coordinate_pareto_frontier_malicious",
                "mean": mean_y_coordinates_pareto_frontier_malicious
            }
        ]

    elif competing_malicious_agents == True: 

        data = [
            {
                "metric": "avg_correction_term_normal_bidders",
                "mean": mean_avg_correction_term_normal_bidders,
                "std": std_avg_correction_term_normal_bidders
            },
            {
                "metric": "optimality",
                "mean": mean_optimality,
                "std": std_optimality
            },
            {
                "metric": "efficiency",
                "mean": mean_efficiency,
                "std": std_efficiency
            },
            {
                "metric": "avg_correction_term_malicious_bidder",
                "mean": mean_avg_correction_term_malicious_bidder,
                "std": std_avg_correction_term_malicious_bidder
            },
            {
                "metric": "malicious",
                "mean": mean_malicious,
                "std": std_malicious
            },
            {
                "metric": "optimality_normal_winner",
                "mean": mean_optimality_normal_winner,
                "std": std_optimality_normal_winner
            },
            {
                "metric": "optimality_malicious_winner",
                "mean": mean_optimality_malicious_winner,
                "std": std_optimality_malicious_winner
            },
            {
                "metric": "efficiency_normal_winner",
                "mean": mean_efficiency_normal_winner,
                "std": std_efficiency_normal_winner
            },
            {
                "metric": "efficiency_malicious_winner",
                "mean": mean_efficiency_malicious_winner,
                "std": std_efficiency_malicious_winner
            }
        ]

    elif competing_malicious_agents == False and x_coordinates_pareto_frontier_dict:

        data = [
            {
                "metric": "avg_correction_term_normal_bidders",
                "mean": mean_avg_correction_term_normal_bidders,
                "std": std_avg_correction_term_normal_bidders
            },
            {
                "metric": "optimality",
                "mean": mean_optimality,
                "std": std_optimality
            },
            {
                "metric": "efficiency",
                "mean": mean_efficiency,
                "std": std_efficiency
            },
            {
                "metric": "x_coordinate_pareto_frontier",
                "mean": mean_x_coordinates_pareto_frontier
            }, 
            {
                "metric": "y_coordinate_pareto_frontier",
                "mean": mean_y_coordinates_pareto_frontier
            }
        ]

    else:
        data = [
            {
                "metric": "avg_correction_term_normal_bidders",
                "mean": mean_avg_correction_term_normal_bidders,
                "std": std_avg_correction_term_normal_bidders
            },
            {
                "metric": "optimality",
                "mean": mean_optimality,
                "std": std_optimality
            },
            {
                "metric": "efficiency",
                "mean": mean_efficiency,
                "std": std_efficiency
            }
        ]

    with open('experiment_results.json', 'w') as json_file:
        json.dump(data, json_file)
    
    # Pareto front
    # Fonts for the graph
    font_title = {
        'family': 'Palatino',
        'weight': 'bold',
        'size': 15
    }

    font_rest = {
        'family': 'Palatino',
        'weight': 'normal',
        'size': 11.5
    }

    font_legend_cm = {
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

    # Plot the average auction outcomes
    if competing_malicious_agents == True:
        colors = ['Green' if malicious[i] == 0 else 'Red' for i in range(1, len(x_coordinates_pareto_frontier) + 1)]
        plt.scatter(x_coordinates_pareto_frontier, y_coordinates_pareto_frontier, label='Data Points', color=colors, edgecolor='Black', marker='o', s=25, zorder=3)
    else:
        plt.scatter(x_coordinates_pareto_frontier, y_coordinates_pareto_frontier, label='Data Points', color="Green", edgecolor='Black', marker='o', s=25, zorder=3)

    # Add the average auction outcomes to the plot
    x_coordinates_pareto_frontier = x_coordinates_pareto_frontier.sort_index()
    y_coordinates_pareto_frontier = y_coordinates_pareto_frontier.sort_index()

    if competing_malicious_agents == True:

        x_coordinates_pareto_frontier_normal_dict = {}
        y_coordinates_pareto_frontier_normal_dict = {}
        x_coordinates_pareto_frontier_malicious_dict = {}
        y_coordinates_pareto_frontier_malicious_dict = {}

        for i in range(1, len(x_coordinates_pareto_frontier) + 1):
            if malicious[i] == 0:
                x_coordinates_pareto_frontier_normal_dict[i] = x_coordinates_pareto_frontier[i]
                y_coordinates_pareto_frontier_normal_dict[i] = y_coordinates_pareto_frontier[i]
            else:
                x_coordinates_pareto_frontier_malicious_dict[i] = x_coordinates_pareto_frontier[i]
                y_coordinates_pareto_frontier_malicious_dict[i] = y_coordinates_pareto_frontier[i]
        
        mean_x_coordinates_pareto_frontier_normal = pd.Series(x_coordinates_pareto_frontier_normal_dict).mean()
        mean_x_coordinates_pareto_frontier_malicious = pd.Series(x_coordinates_pareto_frontier_malicious_dict).mean()
        mean_y_coordinates_pareto_frontier_normal = pd.Series(y_coordinates_pareto_frontier_normal_dict).mean()
        mean_y_coordinates_pareto_frontier_malicious = pd.Series(y_coordinates_pareto_frontier_malicious_dict).mean()

        plt.scatter(mean_x_coordinates_pareto_frontier_normal, mean_y_coordinates_pareto_frontier_normal, label="Data Points", color="LimeGreen", edgecolor="Black", marker='D', s=100, zorder = 4)
        plt.scatter(mean_x_coordinates_pareto_frontier_malicious, mean_y_coordinates_pareto_frontier_malicious, label="Data Points", color="#FFA500", edgecolor="Black", marker='D', s=100, zorder = 4)

    else: 

        plt.scatter(x_coordinates_pareto_frontier.mean(), y_coordinates_pareto_frontier.mean(), label="Data Points", color="LimeGreen", edgecolor="Black", marker='D', s=100, zorder = 4)
    
    # Create the Pareto front and the x and y axis
    plt.plot([1.5, -0.5], [-0.5, 1.5], color='Gray', linestyle='--', label='Pareto Front', zorder=2)
    plt.axhline(0, color='black', linewidth=0.5, zorder=1) 
    plt.axvline(0, color='black', linewidth=0.5, zorder=1) 
    
    # Determine the range of the x and y-axis
    min_x = x_coordinates_pareto_frontier.min()
    max_x = x_coordinates_pareto_frontier.max()
    min_y = y_coordinates_pareto_frontier.min()
    max_y = y_coordinates_pareto_frontier.max()
    extra = 0.03

    plt.xlim(min_x - extra, max_x + extra)
    plt.ylim(min_y - extra, max_y + extra)

    plt.xticks(fontname='Palatino', fontsize=10.5)
    plt.yticks(fontname='Palatino', fontsize=10.5)

    # Set plot labels and title
    plt.xlabel('Utility of the Winning Bidder', fontdict=font_axis)
    plt.ylabel('Utility of the Auctioneer', fontdict=font_axis)
    plt.title("Auction Outcomes Relative to the Pareto Front\n", fontdict=font_title)

    # Create the legend
    if type_of_experiment == "malicious-solo":
        type_of_experiment = "ISB"
    elif type_of_experiment == "malicious-collaborative":
        type_of_experiment = "CSB"
    else:
        type_of_experiment = "Baseline"

    if type_of_experiment == "Baseline":
        label_experiment_type = "Experiment: \n" + type_of_experiment
    else: 
        label_experiment_type = "Experiment: " + type_of_experiment
    label_n = "n = " + str(total_amount_of_bidders)
    label_perc_malicious = "Spiteful Bidders: " + percentage_of_malicious_agents

    if type_of_experiment == "CSB":

        legend_handles = [
            mlines.Line2D([], [], marker='.', color='Black', markeredgecolor='black', markeredgewidth=1, linestyle='None', label=label_experiment_type),
            mlines.Line2D([], [], marker='.', color='Black', markeredgecolor='black', markeredgewidth=1, linestyle='None', label=label_n),
            mlines.Line2D([], [], marker='.', color='Black', markeredgecolor='black', markeredgewidth=1, linestyle='None', label=label_perc_malicious),
            mlines.Line2D([], [], marker='o', color='Green', markersize=8, label='Non-Spiteful Winner', markeredgecolor='black', markeredgewidth=1, linestyle='None'),
            mlines.Line2D([], [], marker='D', color='LimeGreen', markersize=8, label='Mean\nNon-Spiteful Winner', markeredgecolor='black', markeredgewidth=1, linestyle='None'),
            mlines.Line2D([], [], marker='o', color='Red', markersize=8, label='Spiteful Winner', markeredgecolor='black', markeredgewidth=1, linestyle='None'),
            mlines.Line2D([], [], marker='D', color='#FFA500', markersize=8, label='Mean Spiteful Winner', markeredgecolor='black', markeredgewidth=1, linestyle='None'),
            mlines.Line2D([], [], color='Gray', linestyle='--', label='Pareto Front')
        ]
    elif type_of_experiment == "ISB": 

        legend_handles = [
            mlines.Line2D([], [], marker='.', color='Black', markeredgecolor='black', markeredgewidth=1, linestyle='None', label=label_experiment_type),
            mlines.Line2D([], [], marker='.', color='Black', markeredgecolor='black', markeredgewidth=1, linestyle='None', label=label_n),
            mlines.Line2D([], [], marker='.', color='Black', markeredgecolor='black', markeredgewidth=1, linestyle='None', label=label_perc_malicious),
            mlines.Line2D([], [], marker='o', color='Green', markersize=8, label='Auction Outcomes', markeredgecolor='black', markeredgewidth=1, linestyle='None'),
            mlines.Line2D([], [], marker='D', color='LimeGreen', markersize=8, label='Mean', markeredgecolor='black', markeredgewidth=1, linestyle='None'),
            mlines.Line2D([], [], color='Gray', linestyle='--', label='Pareto Front')
        ]
    
    else:

        legend_handles = [
            mlines.Line2D([], [], marker='.', color='Black', markeredgecolor='black', markeredgewidth=1, linestyle='None', label=label_experiment_type),
            mlines.Line2D([], [], marker='.', color='Black', markeredgecolor='black', markeredgewidth=1, linestyle='None', label=label_n),
            mlines.Line2D([], [], marker='o', color='Green', markersize=8, label='Auction\nOutcomes', markeredgecolor='black', markeredgewidth=1, linestyle='None'),
            mlines.Line2D([], [], marker='D', color='LimeGreen', markersize=8, label='Mean', markeredgecolor='black', markeredgewidth=1, linestyle='None'),
            mlines.Line2D([], [], color='Gray', linestyle='--', label='Pareto Front')
        ]

    if competing_malicious_agents == True:
        plt.legend(handles=legend_handles, prop=font_legend_cm, loc="upper right", framealpha=1)
    else:
        plt.legend(handles=legend_handles, prop=font_rest, loc="upper right", framealpha=1)

    # Create the Zoom-Out
    axins = inset_axes(plt.gca(), width="35%", height="35%", loc="lower left")

    min_x = x_coordinates_pareto_frontier.min()
    max_x = x_coordinates_pareto_frontier.max()
    min_y = y_coordinates_pareto_frontier.min()
    max_y = y_coordinates_pareto_frontier.max()
    extra = 0.07

    rect_x_min = min_x - extra
    rect_y_min = min_y - extra
    rect_width = max_x - min_x + 2 * extra
    rect_height = max_y - min_y + 2 * extra

    rect = plt.Rectangle((rect_x_min, rect_y_min), rect_width, rect_height,
                        linewidth=1, edgecolor='Black', facecolor='none', linestyle='-')
    plt.gca().add_patch(rect)

    if competing_malicious_agents:
        colors = ['Green' if malicious[i] == 0 else 'Red' for i in range(1, len(x_coordinates_pareto_frontier) + 1)]
    else:
        colors = 'Green'

    axins.scatter(x_coordinates_pareto_frontier, y_coordinates_pareto_frontier, label='Data Points', color=colors, edgecolor='Black', marker='o', s=9, zorder=3)
    axins.plot([1.2, -0.2], [-0.2, 1.2], color='Gray', linestyle='--', label='Pareto Front',zorder=2)
    axins.axhline(0, color='black', linewidth=0.5, zorder=1)
    axins.axvline(0, color='black', linewidth=0.5, zorder=1) 

    # Some design adjustments
    axins.spines['left'].set_linewidth(1.5)  
    axins.spines['bottom'].set_linewidth(1.5)  
    axins.spines['right'].set_linewidth(1.5)  
    axins.spines['top'].set_linewidth(1.5)  

    plt.xlim(-0.2, 1.2)
    plt.ylim(-0.2, 1.2)
    axins.set_xticks([])
    axins.set_yticks([])
    axins.set_title('Zoom-Out',                 
                    fontdict=font_zoom
    )

    # Save the image in the current directory
    experiment_name = "pareto_front_" + path.split("/")[-1]
    plt.savefig(experiment_name + '.png', dpi=200)