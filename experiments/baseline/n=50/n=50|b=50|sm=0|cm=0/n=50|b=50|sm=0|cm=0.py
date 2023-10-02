import os
import sys

# Get the absolute path to the experiments directory ("move two directories back")
experiments_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','..'))
sys.path.append(experiments_dir + "/python-modules")

from experiment_evaluation_procedure import procedure

current_directory = os.getcwd()

procedure(current_directory)