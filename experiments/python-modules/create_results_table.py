import os
import json
import re
import pandas as pd
from tabulate import tabulate

modules_dir = os.getcwd()
experiments_dir = os.path.abspath(os.path.join(modules_dir, '..'))

order = [
        "Baseline, n=10", "Baseline, n=50", "Baseline, n=100", 
         "Spiteful-Independent (10%), n=10", "Spiteful-Independent (20%), n=10", "Spiteful-Independent (30%), n=10 ", "Spiteful-Independent (40%), n=10", "Spiteful-Independent (50%), n=10",
         "Spiteful-Independent (10%), n=50", "Spiteful-Independent (20%), n=50", "Spiteful-Independent (30%), n=50 ", "Spiteful-Independent (40%), n=50", "Spiteful-Independent (50%), n=50",
         "Spiteful-Independent (10%), n=100", "Spiteful-Independent (20%), n=100", "Spiteful-Independent (30%), n=100 ", "Spiteful-Independent (40%), n=100", "Spiteful-Independent (50%), n=100",
         "Spiteful-Collaborative (10%), n=10", "Spiteful-Collaborative (20%), n=10", "Spiteful-Collaborative (30%), n=10 ", "Spiteful-Collaborative (40%), n=10", "Spiteful-Collaborative (50%), n=10",
         "Spiteful-Collaborative (10%), n=50", "Spiteful-Collaborative (20%), n=50", "Spiteful-Collaborative (30%), n=50 ", "Spiteful-Collaborative (40%), n=50", "Spiteful-Collaborative (50%), n=50",
         "Spiteful-Collaborative (10%), n=100", "Spiteful-Collaborative (20%), n=100", "Spiteful-Collaborative (30%), n=100 ", "Spiteful-Collaborative (40%), n=100", "Spiteful-Collaborative (50%), n=100"
         ]

amount_of_bidders = ["n=10", "n=50", "n=100"]

experiment_index = 0
index_experiments_with_data = []
data = []

# Go through baseline experiments
baseline_dir = os.path.abspath(os.path.join(experiments_dir, 'baseline'))

for bidder_amount in amount_of_bidders:

    general_directory = os.path.abspath(os.path.join(baseline_dir, bidder_amount))
    content_general_directory = os.listdir(general_directory)
    for i in content_general_directory:
        if os.path.isdir(os.path.join(general_directory, i)):
            sd = i
            break
    subdirectory = os.path.abspath(os.path.join(general_directory, sd))

    json_files = [f for f in os.listdir(subdirectory) if f.endswith('.json')]

    if len(json_files) == 1 and json_files[0] == 'experiment_results.json':
        json_file_path = os.path.join(subdirectory, json_files[0])

        with open(json_file_path, 'r') as json_file:
            data.append(json.load(json_file))
            index_experiments_with_data.append(experiment_index)

    experiment_index += 1

# Function for extracting experiment results of malicious-solo and malicious-collaborative cases
def extract_experiment_results(dir, ei):

    for ba in amount_of_bidders:

        general_directory = os.path.abspath(os.path.join(dir, ba))
        content_general_directory = os.listdir(general_directory)
        content_general_directory.sort(reverse=True)

        for i in content_general_directory:

            if os.path.isdir(os.path.join(general_directory, i)):

                subdirectory = os.path.abspath(os.path.join(general_directory, i))

                json_files = [f for f in os.listdir(subdirectory) if f.endswith('.json')]

                if len(json_files) == 1 and json_files[0] == 'experiment_results.json':
                    json_file_path = os.path.join(subdirectory, json_files[0])

                    with open(json_file_path, 'r') as json_file:
                        data.append(json.load(json_file))
                        index_experiments_with_data.append(ei)

                ei += 1

    return ei

# Go through malicious-solo experiments
malicious_solo_dir = os.path.abspath(os.path.join(experiments_dir, 'malicious-solo'))
experiment_index = extract_experiment_results(malicious_solo_dir, experiment_index)

# Go through malicious-collaborative experiments
malicious_collaborative_dir = os.path.abspath(os.path.join(experiments_dir, 'malicious-collaborative'))
experiment_index = extract_experiment_results(malicious_collaborative_dir, experiment_index)

# Create the table
dfs = []
for i, data_row in enumerate(data):
    metric_data = {}
    for entry in data_row:
        metric = entry["metric"]
        if metric in ['efficiency','optimality','malicious','avg_correction_term_normal_bidders','avg_correction_term_malicious_bidder']:
            metric_data[metric] = f"{entry['mean']}"
    df = pd.DataFrame(metric_data, index=[order[index_experiments_with_data[i]]])
    dfs.append(df)

combined_df = pd.concat(dfs, axis=0)
desired_order = ['efficiency','optimality','avg_correction_term_normal_bidders','avg_correction_term_malicious_bidder', 'malicious']
combined_df = combined_df[desired_order]

# Format the DataFrame using tabulate
table_format = tabulate(combined_df, 
                        headers=['Efficiency','Optimality','% Of Wins by Malicious Bidders','Average Correction Term Normal Bidders','Average Correction Term of the Malicious Bidder'], 
                        tablefmt='latex',
                        showindex=True)

print(table_format)












