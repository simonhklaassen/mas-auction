#!/bin/bash

# Set up the CLASSPATH environment variable, compile the java source code files, etc. - see README.md, part 4

##### Experiments
# Define how many bidders should be instantiated and how many experiment rounds should be performed
amountOfNormalBidders=30
amountOfSoloMaliciousBidders=20
amountOfCollusiveMaliciousBidders=0
totalBidders=$((amountOfNormalBidders + amountOfSoloMaliciousBidders + amountOfCollusiveMaliciousBidders))

amountOfRoundsPerExperiment=3

### Path to where the log and result files shall be stored
experimentName="n=${totalBidders}|b=${amountOfNormalBidders}|sm=${amountOfSoloMaliciousBidders}|cm=${amountOfCollusiveMaliciousBidders}"

# Provide your path to the 'mas-auction' directory
pathToLogs="___/mas-auction/experiments/"

### Determine the correct path
# If only normal bidders participate
if [ ! "$amountOfNormalBidders" -eq 0 ] && [ "$amountOfSoloMaliciousBidders" -eq 0 ] && [ "$amountOfCollusiveMaliciousBidders" -eq 0 ]; then
    pathToLogs="${pathToLogs}baseline/"
fi

# If normal and independent spiteful bidders participate
if [ ! "$amountOfNormalBidders" -eq 0 ] && [ ! "$amountOfSoloMaliciousBidders" -eq 0 ] && [ "$amountOfCollusiveMaliciousBidders" -eq 0 ]; then
    pathToLogs="${pathToLogs}malicious-solo/"
fi

# If normal and collaborative spiteful bidders participate
if [ ! "$amountOfNormalBidders" -eq 0 ] && [ "$amountOfSoloMaliciousBidders" -eq 0 ] && [ ! "$amountOfCollusiveMaliciousBidders" -eq 0 ]; then
    pathToLogs="${pathToLogs}malicious-collaborative/"
fi

# Path if n=10
if [ "$totalBidders" -eq 10 ]; then
    pathToLogs="${pathToLogs}n=10/"
fi

# Path if n=50
if [ "$totalBidders" -eq 50 ]; then
    pathToLogs="${pathToLogs}n=50/"
fi

# Path if n=100
if [ "$totalBidders" -eq 100 ]; then
    pathToLogs="${pathToLogs}n=100/"
fi

# Define the folder names
nameExperimentFolder=$(printf "%s%s%s" "$pathToLogs" "$experimentName" "/")
nameExperimentFolderProcess=$(printf "%s%s%s" "$pathToLogs" "$experimentName" "/process/")
nameExperimentFolderResult=$(printf "%s%s%s" "$pathToLogs" "$experimentName" "/result/")

# Create the folders if they do not exist yet
if [ ! -d "$nameExperimentFolder" ]; then
    mkdir "$nameExperimentFolder"
fi

if [ ! -d "$nameExperimentFolderProcess" ]; then
    mkdir "$nameExperimentFolderProcess"
fi

if [ ! -d "$nameExperimentFolderResult" ]; then
    mkdir "$nameExperimentFolderResult"
fi

counterRounds=0

# Run the program
while [ $counterRounds -lt $amountOfRoundsPerExperiment ]; do

    # String to instantiate the auctioneer and the evaluation agent
    result="Seller:English.Auctioneer(${counterRounds}, $nameExperimentFolderProcess);Evaluation-Agent:English.EvaluationAgent(${counterRounds}, $nameExperimentFolderResult)"

    # Append all the strings to instantiate the pre-defined amount the bidder agents
    counterNormalBidders=1
    counterSoloMaliciousBidders=1
    counterCollusiveMaliciousBidders=1

    while [ $counterNormalBidders -le $amountOfNormalBidders ]; do
        result="${result};Bidder${counterNormalBidders}:English.Bidder"
        ((counterNormalBidders++))
    done

    while [ $counterSoloMaliciousBidders -le $amountOfSoloMaliciousBidders ]; do
        result="${result};MaliciousAgentSolo${counterSoloMaliciousBidders}:English.MaliciousAgentSolo"
        ((counterSoloMaliciousBidders++))
    done

    while [ $counterCollusiveMaliciousBidders -le $amountOfCollusiveMaliciousBidders ]; do
        result="${result};MaliciousAgentCollaborative${counterCollusiveMaliciousBidders}:English.MaliciousAgentCollaborative"
        ((counterCollusiveMaliciousBidders++))
    done

    # Run the program
    # Beware: If an experimental setting is run that was examined in the thesis, then the results will be overwritten.
    java $LOGGING_CONFIG jade.Boot -agents "${result}"

    echo "JADE program $((counterRounds + 1)) successfully executed."

    ((counterRounds++))

done

echo "Experiment successfully executed."
