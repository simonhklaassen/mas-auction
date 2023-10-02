import os
import sys
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

current_directory = os.getcwd()

# Get the absolute path to the experiments directory ("move two directories back")
experiments_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
print(experiments_dir)
sys.path.append(experiments_dir + "/python-modules")


from graph_creation import create_graphs
# from cm_optimality_efficiency_table import create_optimality_efficiency_table

current_directory = os.getcwd()

create_graphs(current_directory)

# create_optimality_efficiency_table(current_directory)

# subdirectories = [d for d in os.listdir(current_directory) if os.path.isdir(d)]

# avg_correction_term_normal_bidders_dict = {}
# avg_correction_term_malicious_bidder_dict = {}
# optimality_dict = {}
# efficiency_dict = {}
# malicious_dict = {}

# std_avg_correction_term_normal_bidders_dict = {}
# std_avg_correction_term_malicious_bidder_dict = {}
# std_optimality_dict = {}
# std_efficiency_dict = {}
# std_malicious_dict = {}

# competing_malicious_agents = False
# numbers_after_decimal_point = 3

# for subdirectory in subdirectories:

#     amount_of_agents = re.search(r'n=(\d+)', subdirectory)
#     if amount_of_agents:
#         amount_of_agents = int(amount_of_agents.group(1))

#     amount_of_bidders = re.search(r'b=(\d+)', subdirectory)
#     if amount_of_bidders:
#         amount_of_bidders = int(amount_of_bidders.group(1))


#     print("amount of bidders: " + str(amount_of_bidders))
#     print("amount of agents: " + str(amount_of_agents))

#     percentage_of_malicious_agents = int(round(((1 - (amount_of_bidders / amount_of_agents)) * 100), 1))
#     print("percentage of malicious bidders: " + str(percentage_of_malicious_agents) + "%")
#     percentage_of_malicious_agents = str(percentage_of_malicious_agents) + "%"

#     subdirectory_path = os.path.join(current_directory, subdirectory)
#     json_files = [f for f in os.listdir(subdirectory_path) if f.endswith('.json')]
#     # print("path to .json file: " + json_files[0])

#     if len(json_files) == 1:
#         json_file_path = os.path.join(subdirectory_path, json_files[0])
#         # print(json_file_path)

#         with open(json_file_path, 'r') as json_file:
#                 result_data = json.load(json_file)

#                 for metric in result_data:
                    
#                     if metric["metric"] == "avg_correction_term_normal_bidders":
#                         avg_correction_term_normal_bidders_dict[percentage_of_malicious_agents] = metric["mean"]
#                         std_avg_correction_term_normal_bidders_dict[percentage_of_malicious_agents] = metric["std"]
#                         print("percentage of malicious agents: " + str(percentage_of_malicious_agents) + ", metric: " + metric["metric"] + ", mean: " + str(metric["mean"]) + ", std: " + str(metric["std"]))
                
#                     if metric["metric"] == "optimality":
#                         optimality_dict[percentage_of_malicious_agents] = metric["mean"]
#                         std_optimality_dict[percentage_of_malicious_agents] = metric["std"]
#                         print("percentage of malicious agents: " + str(percentage_of_malicious_agents) + ", metric: " + metric["metric"] + ", mean: " + str(metric["mean"]) + ", std: " + str(metric["std"]))

#                     if metric["metric"] == "efficiency":
#                         efficiency_dict[percentage_of_malicious_agents] = metric["mean"]
#                         std_efficiency_dict[percentage_of_malicious_agents] = metric["std"]
#                         print("percentage of malicious agents: " + str(percentage_of_malicious_agents) + ", metric: " + metric["metric"] + ", mean: " + str(metric["mean"]) + ", std: " + str(metric["std"]))

#                     if metric["metric"] == "avg_correction_term_malicious_bidder":
#                         competing_malicious_agents = True
#                         avg_correction_term_malicious_bidder_dict[percentage_of_malicious_agents] = metric["mean"]
#                         std_avg_correction_term_malicious_bidder_dict[percentage_of_malicious_agents] = metric["std"]
#                         print("percentage of malicious agents: " + str(percentage_of_malicious_agents) + ", metric: " + metric["metric"] + ", mean: " + str(metric["mean"]) + ", std: " + str(metric["std"]))
                    
#                     if metric["metric"] == "malicious":
#                         malicious_dict[percentage_of_malicious_agents] = metric["mean"]
#                         std_malicious_dict[percentage_of_malicious_agents] = metric["std"]
#                         print("percentage of malicious agents: " + str(percentage_of_malicious_agents) + ", metric: " + metric["metric"] + ", mean: " + str(metric["mean"]) + ", std: " + str(metric["std"]))

# ### Also gather data from the respective baseline case

# # Move to the appropriate baseline experiment
# dir_baseline = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..'))
# dir_baseline = dir_baseline + "/baseline/n=" + str(amount_of_agents) + "/n=" + str(amount_of_agents) + "|b=" + str(amount_of_agents) + "|sm=0|cm=0/"
# percentage_of_malicious_agents = "0%"

# files = os.listdir(dir_baseline)

# for file in files:
#     if file.endswith('.json'):
#         json_file = file
#         break

# if json_file:
#     json_file_path = os.path.join(dir_baseline, json_file)
#     with open(json_file_path, 'r') as json_file:
#             result_data = json.load(json_file)

#             for metric in result_data:
                
#                 if metric["metric"] == "avg_correction_term_normal_bidders":
#                     avg_correction_term_normal_bidders_dict[percentage_of_malicious_agents] = metric["mean"]
#                     std_avg_correction_term_normal_bidders_dict[percentage_of_malicious_agents] = metric["std"]
#                     print("percentage of malicious agents: " + str(percentage_of_malicious_agents) + ", metric: " + metric["metric"] + ", mean: " + str(metric["mean"]) + ", std: " + str(metric["std"]))
            
#                 if metric["metric"] == "optimality":
#                     optimality_dict[percentage_of_malicious_agents] = metric["mean"]
#                     std_optimality_dict[percentage_of_malicious_agents] = metric["std"]
#                     print("percentage of malicious agents: " + str(percentage_of_malicious_agents) + ", metric: " + metric["metric"] + ", mean: " + str(metric["mean"]) + ", std: " + str(metric["std"]))

#                 if metric["metric"] == "efficiency":
#                     efficiency_dict[percentage_of_malicious_agents] = metric["mean"]
#                     std_efficiency_dict[percentage_of_malicious_agents] = metric["std"]
#                     print("percentage of malicious agents: " + str(percentage_of_malicious_agents) + ", metric: " + metric["metric"] + ", mean: " + str(metric["mean"]) + ", std: " + str(metric["std"]))
# else:
#     print("No JSON file found in the current directory.")



# ### Convert dictionaries into pandas series
# avg_correction_term_normal_bidders = pd.Series(avg_correction_term_normal_bidders_dict)
# optimality = pd.Series(optimality_dict)
# efficiency = pd.Series(efficiency_dict)
# if competing_malicious_agents == True:
#     avg_correction_term_malicious_bidder = pd.Series(avg_correction_term_malicious_bidder_dict)
#     malicious = pd.Series(malicious_dict)

# std_avg_correction_term_normal_bidders = pd.Series(std_avg_correction_term_normal_bidders_dict)
# std_optimality = pd.Series(std_optimality_dict)
# std_efficiency = pd.Series(std_efficiency_dict)
# if competing_malicious_agents == True:
#     std_avg_correction_term_malicious_bidder = pd.Series(std_avg_correction_term_malicious_bidder_dict)
#     std_malicious = pd.Series(std_malicious_dict)

# ### Reorganize data so that it can be transformed into a DataFrame
# if competing_malicious_agents == True:
#     data = {
#             'Percentage of Wins by Malicious Agents': malicious,
#             'Average Correction Term of the Malicious Bidder': avg_correction_term_malicious_bidder,
#             'Average Correction Term of Normal Bidders': avg_correction_term_normal_bidders,
#             'Efficiency': efficiency,
#             'Optimality': optimality
#             }

#     data_std = {
#             'Percentage of Wins by Malicious Agents': std_malicious,
#             'Average Correction Term of the Malicious Bidder': std_avg_correction_term_malicious_bidder,
#             'Average Correction Term of Normal Bidders': std_avg_correction_term_normal_bidders,
#             'Efficiency': std_efficiency,
#             'Optimality': std_optimality
#             }
# else:
#     data = {
#             'Average Correction Term of Normal Bidders': avg_correction_term_normal_bidders,
#             'Efficiency': efficiency,
#             'Optimality': optimality
#             }

#     data_std = {
#             'Average Correction Term of Normal Bidders': std_avg_correction_term_normal_bidders,
#             'Efficiency': std_efficiency,
#             'Optimality': std_optimality
#             }

# df = pd.DataFrame(data)
# df = df.sort_index(ascending=False)
# df_std = pd.DataFrame(data_std)

# print(df)

# fig, ax = plt.subplots(figsize=(10, 6))



# # ### TO DO Right now the stadard errors are still displayed. In the end, the confidence intervals should be displayed, though.
# bar_plot = df.plot(kind='barh', ax=ax, capsize=4, alpha=0.7, color=['green', 'blue', 'red', 'grey', 'black'], width=0.8) # xerr=df_std, hatch=['\\', '/', '+', '-', '.']

# ax.set_xlim(0,1)
# plt.title('Comparison of Average Auction Outcomes, depending on the Amount of Malicious Bidders')
# # plt.xlabel('Values')
# plt.ylabel('Percentage of malicious Agents')

# bar_plot.legend(loc='upper right')

# # Annotate each bar with its actual value
# # Annotate each bar with its actual value
# # for index, values in enumerate(df.values):
# #     for value in values:
# #         bar_plot.text(value, index, f"{value:.2f}", va='center', color='black', fontsize=9, fontweight='bold', ha='left')

# print(df.values)

# for i, (values, std_values) in enumerate(zip(df.values, df_std.values)):
#     z=0
#     # y_coord = i - 0.34
#     for v, std in zip(values, std_values):
#         y_coord = i - 0.335
#         # Adjust the y-coordinate to be at the height of the bar
#         x_coord = v + 0.01
#         # y_coord = i + 0.2  # You may need to adjust this value to position the annotation correctly
#         bar_plot.annotate(f'{v:.2f}', xy=(x_coord, y_coord + 0.10 * 1.6 * z), va='center', color='gray', fontsize=7, fontweight='bold')
#         z += 1
# # Add labels to the bars with exact values
# # Add labels to the bars with exact values
# # for i, (v, std) in enumerate(zip(df.values, df_std.values)):
# #     bar_plot.text(v + std + 0.01, i, f' {v:.2f}', va='center', color='black', fontsize=9, fontweight='bold', ha='left')


# plt.show()

# ### Plot with Seaborn

# # Create a bar plot using Seaborn
# # sns.set(style="whitegrid")  # Set the plot style

# # # Create the bar plot
# # plt.figure(figsize=(8, 6))  # Set the figure size (optional)
# # sns.barplot(data=df)

# # # Add labels and title
# # plt.xlabel('Categories')
# # plt.ylabel('Values')
# # plt.title('Bar Plot Example')

# # # Show the plot
# # plt.show()

# # data = {
# #     'Category': ['A', 'B', 'C', 'D'],
# #     'Value': [10, 25, 15, 30]
# # }

# # dfex = pd.DataFrame(data)
# # print(dfex)

# # Create a grouped bar plot using Seaborn
# # sns.set(style="whitegrid")  # Set the plot style

# # ax = sns.barplot(x="Efficiency", y=df.index, data=df, orient="h", label='Percentage of Wins')


# # plt.show()


# # # Create the bar graph
# # ax = df.plot(kind='barh', figsize=(10, 6))

# # # Set labels and title
# # ax.set_xlabel('Values')
# # ax.set_ylabel('Index')
# # ax.set_title('Bar Graph of Values by Index')

# # # Display the legend
# # ax.legend(loc='best')

# # # Show the plot
# # plt.show()
























# ### Calculate means
# # mean_avg_correction_term_normal_bidders = round(avg_correction_term_normal_bidders.mean(), numbers_after_decimal_point)
# # mean_optimality = round(optimality.mean(), numbers_after_decimal_point)
# # mean_efficiency = round(efficiency.mean(), numbers_after_decimal_point)
# # if competing_malicious_agents:
# #     mean_malicious = round(malicious.mean(), numbers_after_decimal_point)
# #     mean_avg_correction_term_malicious_bidder = round(avg_correction_term_malicious_bidder.mean(), numbers_after_decimal_point)

# ### Calculate standard deviations
# # std_avg_correction_term_normal_bidders = round(avg_correction_term_normal_bidders.std(), numbers_after_decimal_point)
# # std_optimality = round(optimality.std(), numbers_after_decimal_point)
# # std_efficiency = round(efficiency.std(), numbers_after_decimal_point)
# # if competing_malicious_agents == True:
# #     std_malicious = round(malicious.std(), numbers_after_decimal_point)
# #     std_avg_correction_term_malicious_bidder = round(avg_correction_term_malicious_bidder.std(), numbers_after_decimal_point)


# ### Print results
# # Mean
# # print("### Means ###")
# # print(f"Average correction term of normal bidders throughout the experiment: {mean_avg_correction_term_normal_bidders}.")
# # print(f"Average optimality: {mean_optimality}")
# # print(f"Average efficiency: {mean_efficiency}")
# # if competing_malicious_agents == True:
# #     print(f"Average correction term of the malicious bidder throughout the experiment: {mean_avg_correction_term_malicious_bidder}")
# #     print(f"Percentage of wins by the malicious bidding ring: {mean_malicious}")

# # Standard deviation
# # print("### Standard Deviations ###")
# # print(f"Standard deviation of correction term of normal bidders: {std_avg_correction_term_normal_bidders}.")
# # print(f"Standard deviation optimality: {std_optimality}")
# # print(f"Standard deviation efficiency: {std_efficiency}")
# # if competing_malicious_agents:
# #     print(f"Standard deviation of correction term of the malicious bidder: {std_avg_correction_term_malicious_bidder}")
# #     print(f"Standard Deviation of percentage of wins by the malicious bidding ring: {std_malicious}")

# ### Store results in a .json file.
# # Format data in a way so that it can be transformed into a json array.
# # if competing_malicious_agents == True:
# #     data = [
# #         {
# #             "metric": "average_correction_term_normal_bidders",
# #             "mean": mean_avg_correction_term_normal_bidders,
# #             "std": std_avg_correction_term_normal_bidders
# #         },
# #         {
# #             "metric": "optimality",
# #             "mean": mean_optimality,
# #             "std": std_optimality
# #         },
# #         {
# #             "metric": "efficiency",
# #             "mean": mean_efficiency,
# #             "std": std_efficiency
# #         },
# #         {
# #             "metric": "avg_avg_correction_term_malicious_bidder",
# #             "mean": mean_avg_correction_term_malicious_bidder,
# #             "std": std_avg_correction_term_malicious_bidder
# #         },
# #         {
# #             "metric": "malicious",
# #             "mean": mean_malicious,
# #             "std": std_malicious
# #         }
# #     ]

# # else:
# #     data = [
# #         {
# #             "metric": "average_correction_term_normal_bidders",
# #             "mean": mean_avg_correction_term_normal_bidders,
# #             "std": std_avg_correction_term_normal_bidders
# #         },
# #         {
# #             "metric": "optimality",
# #             "mean": mean_optimality,
# #             "std": std_optimality
# #         },
# #         {
# #             "metric": "efficiency",
# #             "mean": mean_efficiency,
# #             "std": std_efficiency
# #         }
# #     ]

# # with open('experiment_results.json', 'w') as json_file:
# #     json.dump(data, json_file)
