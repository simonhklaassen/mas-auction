import os
import sys

# Get the absolute path to the experiments directory ("move two directories back")
experiments_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','..'))
sys.path.append(experiments_dir + '/python-modules')

from experiment_evaluation_procedure import procedure

current_directory = os.getcwd()

procedure(current_directory)

# import os
# import json
# import re
# import pandas as pd

# directory_experiment_results = os.path.dirname(__file__) + "/result/"

# ### Create a list of all json files stored in the current 
# list_json_files = os.listdir(directory_experiment_results)
# amount_of_json_files = 0

# problem_complexity_dict = {}
# problem_size_dict = {}
# avg_correction_term_normal_bidders_dict = {}
# avg_correction_term_malicious_bidder_dict = {}
# optimality_dict = {}
# efficiency_dict = {}
# malicious_dict = {}

# competing_malicious_agents = False
# numbers_after_decimal_point = 3


# for filename in list_json_files:

#     if filename.endswith('.json'):

#         file_path = os.path.join(directory_experiment_results, filename)
#         amount_of_json_files += 1

#         ### Extract the experiment nr
#         match = re.search(r'experiment(\d+)\.json', filename)

#         if match:
#             exp_nr = int(match.group(1))
#             # print(exp_nr)

#         ### Open the .json file and store auction results in dictionaries, using the experiment nr as the index.
#         with open(file_path, 'r') as json_file:

#             result_data = json.load(json_file)
            
#             problem_complexity_dict[exp_nr] = result_data["problem_complexity"]
#             problem_size_dict[exp_nr] = result_data["problem_size"]
#             avg_correction_term_normal_bidders_dict[exp_nr] = result_data["avg_correction_term_normal_bidders"]
#             optimality_dict[exp_nr] = result_data["optimality"]
#             efficiency_dict[exp_nr] = result_data["efficiency"]
#             if "avg_correction_term_malicious_bidder" in result_data:
#                 avg_correction_term_malicious_bidder_dict[exp_nr] = result_data["avg_correction_term_malicious_bidder"]
#                 competing_malicious_agents = True
#             if "malicious" in result_data: 
#                 malicious_dict[exp_nr] = result_data["malicious"]

#             # print(result_data["efficiency"])

# ### Convert dictionaries into pandas series
# problem_complexity = pd.Series(problem_complexity_dict)
# problem_size = pd.Series(problem_size_dict)
# avg_correction_term_normal_bidders = pd.Series(avg_correction_term_normal_bidders_dict)
# optimality = pd.Series(optimality_dict)
# efficiency = pd.Series(efficiency_dict)
# if competing_malicious_agents == True:
#     avg_correction_term_malicious_bidder = pd.Series(avg_correction_term_malicious_bidder_dict)
#     malicious = pd.Series(malicious_dict)

# ### Calculate means
# mean_avg_correction_term_normal_bidders = round(avg_correction_term_normal_bidders.mean(), numbers_after_decimal_point)
# mean_optimality = round(optimality.mean(), numbers_after_decimal_point)
# mean_efficiency = round(efficiency.mean(), numbers_after_decimal_point)
# if competing_malicious_agents:
#     mean_malicious = round(malicious.mean(), numbers_after_decimal_point)
#     mean_avg_correction_term_malicious_bidder = round(avg_correction_term_malicious_bidder.mean(), numbers_after_decimal_point)

# ### Calculate standard deviations
# std_avg_correction_term_normal_bidders = round(avg_correction_term_normal_bidders.std(), numbers_after_decimal_point)
# std_optimality = round(optimality.std(), numbers_after_decimal_point)
# std_efficiency = round(efficiency.std(), numbers_after_decimal_point)
# if competing_malicious_agents == True:
#     std_malicious = round(malicious.std(), numbers_after_decimal_point)
#     std_avg_correction_term_malicious_bidder = round(avg_correction_term_malicious_bidder.std(), numbers_after_decimal_point)


# ### Print results
# # Mean
# print("### Means ###")
# print(f"Average correction term of normal bidders throughout the experiment: {mean_avg_correction_term_normal_bidders}.")
# print(f"Average optimality: {mean_optimality}")
# print(f"Average efficiency: {mean_efficiency}")
# if competing_malicious_agents == True:
#     print(f"Average correction term of the malicious bidder throughout the experiment: {mean_avg_correction_term_malicious_bidder}")
#     print(f"Percentage of wins by the malicious bidding ring: {mean_malicious}")

# # Standard deviation
# print("### Standard Deviations ###")
# print(f"Standard deviation of correction term of normal bidders: {std_avg_correction_term_normal_bidders}.")
# print(f"Standard deviation optimality: {std_optimality}")
# print(f"Standard deviation efficiency: {std_efficiency}")
# if competing_malicious_agents:
#     print(f"Standard deviation of correction term of the malicious bidder: {std_avg_correction_term_malicious_bidder}")
#     print(f"Standard Deviation of percentage of wins by the malicious bidding ring: {std_malicious}")

# ### Store results in a .json file.
# # Format data in a way so that it can be transformed into a json array.
# if competing_malicious_agents == True:
#     data = [
#         {
#             "metric": "avg_correction_term_normal_bidders",
#             "mean": mean_avg_correction_term_normal_bidders,
#             "std": std_avg_correction_term_normal_bidders
#         },
#         {
#             "metric": "optimality",
#             "mean": mean_optimality,
#             "std": std_optimality
#         },
#         {
#             "metric": "efficiency",
#             "mean": mean_efficiency,
#             "std": std_efficiency
#         },
#         {
#             "metric": "avg_correction_term_malicious_bidder",
#             "mean": mean_avg_correction_term_malicious_bidder,
#             "std": std_avg_correction_term_malicious_bidder
#         },
#         {
#             "metric": "malicious",
#             "mean": mean_malicious,
#             "std": std_malicious
#         }
#     ]

# else:
#     data = [
#         {
#             "metric": "avg_correction_term_normal_bidders",
#             "mean": mean_avg_correction_term_normal_bidders,
#             "std": std_avg_correction_term_normal_bidders
#         },
#         {
#             "metric": "optimality",
#             "mean": mean_optimality,
#             "std": std_optimality
#         },
#         {
#             "metric": "efficiency",
#             "mean": mean_efficiency,
#             "std": std_efficiency
#         }
#     ]

# with open('experiment_results.json', 'w') as json_file:
#     json.dump(data, json_file)
