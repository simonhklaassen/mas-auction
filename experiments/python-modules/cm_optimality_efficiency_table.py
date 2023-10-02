import os
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

def create_optimality_efficiency_table(current_directory):

    # Gather Relevant Data
    subdirectories = [d for d in os.listdir(current_directory) if os.path.isdir(d)]

    optimality_malicious_winner_dict = {}
    optimality_normal_winner_dict = {}
    efficiency_malicious_winner_dict = {}
    efficiency_normal_winner_dict = {}

    numbers_after_decimal_point = 3

    for subdirectory in subdirectories:

        amount_of_agents = re.search(r'n=(\d+)', subdirectory)
        if amount_of_agents:
            amount_of_agents = int(amount_of_agents.group(1))

        amount_of_bidders = re.search(r'b=(\d+)', subdirectory)
        if amount_of_bidders:
            amount_of_bidders = int(amount_of_bidders.group(1))

        percentage_of_malicious_bidders = int(round(((1 - (amount_of_bidders / amount_of_agents)) * 100), 1))
        percentage_of_malicious_bidders = str(percentage_of_malicious_bidders) + "%"

        subdirectory_path = os.path.join(current_directory, subdirectory)
        json_files = [f for f in os.listdir(subdirectory_path) if f.endswith('.json')]

        if len(json_files) == 1:
            json_file_path = os.path.join(subdirectory_path, json_files[0])

            with open(json_file_path, 'r') as json_file:
                    result_data = json.load(json_file)

                    for metric in result_data:
                        
                        if metric["metric"] == "optimality_normal_winner":
                            optimality_normal_winner_dict[percentage_of_malicious_bidders] = f"{metric['mean']} ({metric['std']})"
                        
                        if metric["metric"] == "optimality_malicious_winner":
                            optimality_malicious_winner_dict[percentage_of_malicious_bidders] = f"{metric['mean']} ({metric['std']})"

                        if metric["metric"] == "efficiency_normal_winner":
                            efficiency_normal_winner_dict[percentage_of_malicious_bidders] = f"{metric['mean']} ({metric['std']})"

                        if metric["metric"] == "efficiency_malicious_winner":
                            efficiency_malicious_winner_dict[percentage_of_malicious_bidders] = f"{metric['mean']} ({metric['std']})"

    optimality_normal_winner = pd.Series(optimality_normal_winner_dict)
    optimality_malicious_winner = pd.Series(optimality_malicious_winner_dict)
    efficiency_normal_winner = pd.Series(efficiency_normal_winner_dict)
    efficiency_malicious_winner = pd.Series(efficiency_malicious_winner_dict)

    # Reorganize data so that it can be transformed into a DataFrame
    data = {
                'Optimality if Winner is a Normal Bidder': optimality_normal_winner,
                'Optimality if Winner is a Malicious Bidder': optimality_malicious_winner,
                'Efficiency if Winner is a Normal Bidder': efficiency_normal_winner,
                'Efficiency if Winner is a Malicious Bidder': efficiency_malicious_winner
                }

    df = pd.DataFrame(data)
    df = df.sort_index(ascending=False)
    df = df[['Efficiency if Winner is a Normal Bidder',
        'Efficiency if Winner is a Malicious Bidder',
        'Optimality if Winner is a Normal Bidder',
        'Optimality if Winner is a Malicious Bidder']]

    df_efficiency = (df.T).head(2)
    df_efficiency = df_efficiency[['10%', '20%', '30%', '40%', '50%']]
    df_optimality = (df.T).iloc[2:4]
    df_optimality = df_optimality[['10%', '20%', '30%', '40%', '50%']]

    # Efficiency Table
    table_efficiency = tabulate(df_efficiency, 
                        headers=['10%', '20%', '30%', '40%', '50%'],
                        tablefmt='fancy_grid',
                        showindex=True)
    
    print(table_efficiency)

    # Optimality Table
    table_optimality = tabulate(df_optimality, 
                        headers=['10%', '20%', '30%', '40%', '50%'],
                        tablefmt='fancy_grid',
                        showindex=True)
    
    print(table_optimality)