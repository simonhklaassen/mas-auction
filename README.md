# 1 Overview

This directory contains the implementation of the English auction that was used for the experimental analysis in the Bachelor's thesis "Bidders With Spite Towards the Auctioneer - An Experimental Study on Cloud Service Auctions" by Simon Klaassen. 

# 2 Navigation

In folder 'src/English', all the java source code files are stored that contain the code for the auctioneer agent, the normal bidder agents, both types of spiteful bidder agents, and the evaluation agent. The experiment results and graphs that were used in the thesis can be found in the 'experiments' folder. The rest should be self-explanatory.

# 3 Installation Instructions

To run this Java project, the JADE library can either be installed (https://jade.tilab.com/download/jade/), or the JADE library included in the repository can be used. For JADE to work, a complete Java programming environment is needed. At least a Java Development Kit version 1.4 is required. Finally, to be able to work with JSON, the org.json package has to be downloaded as well (https://github.com/stleary/JSON-java/blob/master/README.md).

# 4 Running Instructions

1. First, all the .jar-files that can be found in the "lib" directory of the downloaded JADE library have to be added to the CLASSPATH environment variable. The .jar-file from the org.json package has to be added to the CLASSPATH environment variable as well (the version from June 18th, 2023 was used in this project). Finally, the Java source code files have to be compiled and included in the CLASSPATH environment variable, too. <br><br>So far, it could look something like this (replace "_____" with the respective paths to those files and directories)

    ``````bash
    export CLASSPATH=_____/jade/lib/jade.jar:_____/jade/lib/commons-codec/commons-codec-1.3.jar:/_____/json-20230618.jar

    cd _____/mas-auction/src/English

    javac -d ../../bin *.java

    export CLASSPATH=_____/mas-auction/bin:_____/jade/lib/jade.jar:_____/jade/lib/commons-codec/commons-codec-1.3.jar:/_____/json-20230618.jar 
    ```````

2. To format the logs of the auctioning process more nicely, the logging configuration can be changed to the configuration defined in the 'logging.properties'-file (replace "_____" with the path to the file)
    ``````bash
    LOGGING_CONFIG="-Djava.util.logging.config.file=_____/mas-auction/src/English/logging.properties"
    ```````
    
3. Now, the amount and types of agents that should be instantiated have to be defined. In every auction, one auctioneer agent, one evaluation agent, and at least two bidders agents have to be instantiated. 
        
    - The auctioneer agent requires two input parameters: The type of computational task and the path to the directory where the log of the auctioning process should be stored. For the type of computational task, any integer between 0 and 23 is a valid argument (any of the 24 computational tasks that were investigated in the paper).

    - The evaluation agent requires the same input parameters, but here the path argument declares where the .json-file with the results will be stored.

    - Normal and spiteful bidder agents don't require input parameters.

    Below, three examples of agent declarations are given (Replace "_____" with the respective paths to the directories)

    - Ten normal bidder agents.

        ``````bash
        Seller:English.Auctioneer(0, _____);Evaluation-Agent:English.EvaluationAgent(0, _____);Bidder1:English.Bidder;Bidder2:English.Bidder;Bidder3:English.Bidder;Bidder4:English.Bidder;Bidder5:English.Bidder;Bidder6:English.Bidder;Bidder7:English.Bidder;Bidder8:English.Bidder;Bidder9:English.Bidder;Bidder10:English.Bidder
        ```````

    - Five normal bidder agents, five independent spiteful agents

        ``````bash
        Seller:English.Auctioneer(8, _____);Evaluation-Agent:English.EvaluationAgent(8, _____);Bidder1:English.Bidder;Bidder2:English.Bidder;Bidder3:English.Bidder;Bidder4:English.Bidder;Bidder5:English.Bidder;MaliciousAgentSolo1:English.MaliciousAgentSolo;MaliciousAgentSolo2:English.MaliciousAgentSolo;MaliciousAgentSolo3:English.MaliciousAgentSolo;MaliciousAgentSolo4:English.MaliciousAgentSolo;MaliciousAgentSolo5:English.MaliciousAgentSolo
        ```````

    - Five normal bidder agents, five collaborative spiteful agents

        ``````bash
        Seller:English.Auctioneer(16, _____);Evaluation-Agent:English.EvaluationAgent(16, _____);Bidder1:English.Bidder;Bidder2:English.Bidder;Bidder3:English.Bidder;Bidder4:English.Bidder;Bidder5:English.Bidder;MaliciousAgentSolo1:English.MaliciousAgentSolo;MaliciousAgentSolo2:English.MaliciousAgentSolo;MaliciousAgentSolo3:English.MaliciousAgentSolo;MaliciousAgentSolo4:English.MaliciousAgentSolo;MaliciousAgentSolo5:English.MaliciousAgentSolo
        ```````

4. JADE can then be launched by executing the following command (Replace ____ with a string containing the agent declarations, for instance the examples given above)

    ``````bash
    java $LOGGING_CONFIG jade.Boot -agents "_____"
    ```````
