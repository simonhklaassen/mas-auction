package English;

import jade.core.AID;
import jade.core.Agent;
import jade.core.behaviours.Behaviour;
import jade.core.behaviours.OneShotBehaviour;
import jade.domain.DFService;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.domain.FIPAAgentManagement.ServiceDescription;
import jade.domain.FIPAException;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.MessageTemplate;

import java.io.IOException;
import java.text.DecimalFormat;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.logging.Logger;
import java.util.logging.FileHandler;
import java.util.logging.Level;
import java.util.concurrent.ThreadLocalRandom;

public class Auctioneer extends Agent {

    private AID[] bidderAgents;
    private Integer amountOfBidders;
    private AID evaluationAgent;

    private String itemName;
    private int[] problemSizes = Configuration.problemSizes;
    private Integer problemSize;
    private String[] problemComplexities = Configuration.problemComplexities;
    private String problemComplexity;
    private Double taskCostliness;
    private Double alpha = Configuration.alpha;
    private Double beta = Configuration.beta;
    private double gamma = Configuration.gamma;

    private Double factorInitialPrice = 1 + alpha;
    private Long startingPrice;

    private Integer decimalPlacesRounding = 3;
    DecimalFormat decimalFormat = new DecimalFormat("0." + "0".repeat(decimalPlacesRounding));

    private String[] complexityForEachExperimentRound;
    private int[] problemSizeForEachExperimentRound;
    private int experimentRound;
    private String storageDirectoryLogFile;

    Logger logger = Logger.getLogger("AuctionLogger");

    @Override
    protected void setup() {  

        Object[] args = getArguments();

        if (args != null && args.length > 0) {

            // Store the input parameters in variables
            experimentRound = Integer.parseInt((String) args[0]);
            storageDirectoryLogFile = (String) args[1];

            initiateLogger(logger);

            // Determine task size and task complexity
            complexityForEachExperimentRound = generateListWithTaskComplexities(problemComplexities, problemSizes, Configuration.amountOfTasksPerCombination);
            problemSizeForEachExperimentRound = generateListWithTaskProblemSizes(problemComplexities, problemSizes, Configuration.amountOfTasksPerCombination);
            problemComplexity = complexityForEachExperimentRound[experimentRound];
            problemSize = problemSizeForEachExperimentRound[experimentRound];
            itemName = "(" + problemComplexity + ", " + problemSize + ")";

            // Log relevant information
            taskCostliness = setTaskCostliness(gamma);
            logger.info("Auction Protocol\n\n");
            logger.info("Auctioneer: Complexity of the task to be auctioned: " + problemComplexity + "\n");
            logger.info("Auctioneer: Problem size of the task to be auctioned: " + problemSize + "\n");
            logger.info("Auctioneer: The costliness factor of the task to be auctioned (unknown to bidders): " + taskCostliness + "\n");
            logger.info("Auctioneer: Hardware coefficients are uniformly distributed between: [" + decimalFormat.format((1-alpha)) + ", " + (1+alpha) + "]\n");
            logger.info("Auctioneer: Bidders know that their estimates of the task costliness are off by at most: " + beta + " in both directions\n");

            // Calculate the starting price of the auction.
            calculateInitialPrice(problemSize, problemComplexity, taskCostliness, factorInitialPrice);
            logger.info("Auctioneer: The starting price of the auction is: $" + startingPrice + "\n");

            // Register the auctioneer in the yellow pages
            DFAgentDescription dfd = new DFAgentDescription();
            dfd.setName(getAID());
            ServiceDescription sdAuctioneer = new ServiceDescription();
            sdAuctioneer.setName("Auctioneer");
            sdAuctioneer.setType("-");
            dfd.addServices(sdAuctioneer);
            try {
                DFService.register(this, dfd);
            } catch (FIPAException e) {
                e.printStackTrace();
            }

            // Find all registered bidders using the yellow pages.
            addBehaviour(new OneShotBehaviour() {

                @Override
                public void action() {

                    DFAgentDescription templateBidder = new DFAgentDescription();
                    ServiceDescription sdBidder = new ServiceDescription();
                    sdBidder.setName("Bidder");
                    templateBidder.addServices(sdBidder);

                    try {
                        DFAgentDescription[] result = DFService.search(myAgent, templateBidder);
                        bidderAgents = new AID[result.length];
                        amountOfBidders = result.length;
                        for (int i = 0; i < result.length; i++) {
                            bidderAgents[i] = result[i].getName();
                        }
                        if (result.length == 0) {
                            logger.log(Level.INFO, "No registered bidder could be found.\n");
                        }
                    } catch (FIPAException e) {
                        e.printStackTrace();
                    }

                    // Find the evaluation agent
                    DFAgentDescription templateEvaluationAgent = new DFAgentDescription();
                    ServiceDescription sdEvaluationAgent = new ServiceDescription();
                    sdEvaluationAgent.setName("Evaluation-Agent");
                    templateEvaluationAgent.addServices(sdEvaluationAgent);

                    try {
                        DFAgentDescription[] result = DFService.search(myAgent, templateEvaluationAgent);
                        if (result.length == 0) {
                            logger.log(Level.INFO, "No registered evaluation agent could be found.\n");
                        } else {
                            evaluationAgent = result[0].getName();
                        }
                    } catch (FIPAException e) {
                        e.printStackTrace();
                    }

                    // Add the behavior of an auctioneer, described below
                    myAgent.addBehaviour(new AuctionPerformer());
                    }
                });
            } else {
                System.out.println("Wrong input, program is aborted.");
                doDelete();
                System.exit(0);
            }
    }

    private String[] generateListWithTaskComplexities (String[] pc, int[] ps, int aotpc) {

        int amountOfExperimentRounds = pc.length * ps.length * aotpc;
        String[] complexityForEachExperimentRound = new String[amountOfExperimentRounds];

        int tasksPerComplexity = amountOfExperimentRounds / pc.length;

        int k = 0;
        for (int i = 0; i < pc.length; i++) {
            for (int j = 0; j < tasksPerComplexity; j++) {
                complexityForEachExperimentRound[k] = pc[i];
                k++;
            } 
        }
        return complexityForEachExperimentRound;
    }

    private int[] generateListWithTaskProblemSizes (String[] pc, int[] ps, int aotpc) {

        int amountOfExperimentRounds = pc.length * ps.length * aotpc;
        int[] problemSizeForEachExperimentRound = new int[amountOfExperimentRounds];

        int tasksPerProblemSize = amountOfExperimentRounds / ps.length;

        int k = 0;
        for (int i = 0; i < tasksPerProblemSize; i++) {
            for (int j = 0; j < ps.length; j++) {
                problemSizeForEachExperimentRound[k] = ps[j];
                k++;
            } 
        }
        return problemSizeForEachExperimentRound;
    }

    private Double setTaskCostliness(Double g) {

        Double max = 1 + gamma;
        Double min = 1 - gamma;
        Double tc = ThreadLocalRandom.current().nextDouble(min, max);
        tc = Double.parseDouble(decimalFormat.format(tc));

        return tc;
    }

    private void calculateInitialPrice(long ps, String pc, double tc, double f) {

        if (pc == "logn") {
            startingPrice = (long) Math.ceil(Math.log(ps) / Math.log(2));
        } else if (pc == "linear") {
            startingPrice = ps;
        } else if (pc == "nlogn") {
            startingPrice = (long) Math.ceil((Math.log(ps) / Math.log(2)) * ps);
        } else {
            startingPrice = (long) Math.pow(ps, 2);
        }
        startingPrice = (long) Math.ceil(((double) startingPrice) * tc * f);
    }

    private void initiateLogger(Logger lg) {
        try {
            // String directoryPath = "/Users/simonklaassen/Documents/bildung/06-ba-uzh-bwl/6-semester/bachelor-thesis/MAS/baseline-model/logs/";
            String directoryPath = storageDirectoryLogFile;
            FileHandler fileHandler = new FileHandler(directoryPath + "experiment" + (experimentRound+1) + ".log"); // could include a time stamp such that log files are never overwritten
            CustomFormatter formatter = new CustomFormatter();
            fileHandler.setFormatter(formatter);
            lg.addHandler(fileHandler);
        } catch (IOException e) {
            e.printStackTrace();
        }  
    }

    @Override
    protected void takeDown() {
        try {
            DFService.deregister(this);
        } catch (FIPAException e) {
            e.printStackTrace();
        }
        logger.log(Level.INFO, "Auctioneer " + getAID().getName() + " terminating.\n");
        doDelete();
    }

    private class AuctionPerformer extends Behaviour {
        private int step = 0;
        private Map<AID, Integer> receivedReplies = new HashMap<>();
        private int numExpectedReplies = 0;
        private int amountOfBids = 0;
        private int increment = -((int) Math.ceil(((double) startingPrice) / 50.0));
        private int roundNr;

        private MessageTemplate mt;
        private MessageTemplate mtSealedBid;
        private AID[] lowestBidders = Arrays.copyOf(bidderAgents,bidderAgents.length);
        private AID[] lowestBiddersLastRound;
        private long lowestBid = Long.MAX_VALUE;
        private int amountOfRecipients;

        @Override
        public void action() {

            switch (step) {

                case 0:

                    // Send all bidder agents the relevant information about the computational task that is auctioned.
                    ACLMessage inf = new ACLMessage(ACLMessage.INFORM);
                    inf.setContent(problemSize + "||" + problemComplexity + "||" + taskCostliness + "||" + amountOfBidders);
                    for (int i = 0; i < bidderAgents.length; i++) {
                        inf.addReceiver(bidderAgents[i]);
                    }
                    inf.setConversationId("information computational task");
                    myAgent.send(inf);

                    roundNr = 1;

                    step = 1;
                    break;

                case 1:

                    // Variables that are overwritten each auction round
                    receivedReplies = new HashMap<>();
                    numExpectedReplies = 0;
                    amountOfBids = 0;
                    lowestBiddersLastRound = Arrays.copyOf(lowestBidders,lowestBidders.length);

                    // Send a call for proposals to bidders along with the current bid price
                    ACLMessage cfp = new ACLMessage(ACLMessage.CFP);

                    for (int i = 0; i < lowestBidders.length; i++) {
                        
                        // Check if the bidder bid in the last round. If yes, add as receiver
                        if (lowestBidders[i] != null) {
                            cfp.addReceiver(lowestBidders[i]);
                            numExpectedReplies++;
                        }

                    }  

                    if (lowestBid < startingPrice) {
                        cfp.setContent(itemName + "||" + lowestBid + "||" + numExpectedReplies + "||" + roundNr);
                    } else {
                        cfp.setContent(itemName + "||" + startingPrice + "||" + amountOfBidders + "||" + roundNr);
                    }

                    cfp.setConversationId("cfp english auction");
                    cfp.setReplyWith("cfp" + System.currentTimeMillis());
                    myAgent.send(cfp);

                    // Create a template for receiving proposals and refusals from bidders
                    mt = MessageTemplate.and(
                            MessageTemplate.MatchConversationId("cfp english auction"),
                            MessageTemplate.MatchInReplyTo(cfp.getReplyWith()));

                    step = 2;
                    break;

                case 2:
                    
                    // The auctioneer receives all replies that match the message template.
                    ACLMessage reply = myAgent.receive(mt);

                    // Go through all responses
                    if (reply != null) {
                        
                        switch (reply.getPerformative()) {

                            // If a bidders decided to bid
                            case ACLMessage.PROPOSE:

                                receivedReplies.put(reply.getSender(), Integer.parseInt(reply.getContent()));
                                logger.log(Level.INFO, reply.getSender().getName() + ": I bid $" + reply.getContent()+"\n");
                                amountOfBids++;
                                break;
                            
                            // If a bidder refused to bid
                            case ACLMessage.REFUSE:
                                receivedReplies.put(reply.getSender(), null);
                                logger.log(Level.INFO, reply.getSender().getName() + ": I don't want to bid the current ask price\n");
                                for (int i=0; i<lowestBidders.length; i++) {
                                    if (lowestBidders[i] != null){
                                        if (lowestBidders[i].equals(reply.getSender())) {
                                            lowestBidders[i] = null;
                                        }
                                    }
                                }

                                break;
                        }
                        // Progress once all replies have been answered
                        if (receivedReplies.size() == numExpectedReplies) {
                            step = 3;
                        }

                    } else {
                        block();
                    }
                    break;

                case 3:

                    // Go through all bids and update what the lowest bid is so far
                    Iterator<Map.Entry<AID, Integer>> iter = receivedReplies.entrySet().iterator();
                    while (iter.hasNext()) {

                        Map.Entry<AID, Integer> item = iter.next();
                        if (item.getValue() != null) {
                            lowestBid = item.getValue();
                            break;
                        }
                    }

                    printBidders(amountOfBids);

                    // Send acceptance of proposal to the highest bidders
                    ACLMessage accept = new ACLMessage(ACLMessage.ACCEPT_PROPOSAL);
                    for (int i = 0; i < lowestBidders.length; i++) {
                        if (lowestBidders[i] != null) {
                            accept.addReceiver(lowestBidders[i]);
                        }
                    }
                    accept.setContent(itemName + "||" + lowestBid);
                    accept.setConversationId("auction");
                    accept.setReplyWith("bid-ok" + System.currentTimeMillis());
                    myAgent.send(accept);
                    
                    // Send a rejection to all bidders that refused to bid
                    Iterator<Map.Entry<AID, Integer>> iter2 = receivedReplies.entrySet().iterator();
                    while (iter2.hasNext()) {

                        Map.Entry<AID, Integer> entry = iter2.next();
                        if (entry.getValue() == null) {
                            ACLMessage reject = new ACLMessage(ACLMessage.REJECT_PROPOSAL);
                            reject.addReceiver(entry.getKey());
                            reject.setContent(itemName + "||" + entry.getKey());
                            reject.setConversationId("auction");
                            reject.setReplyWith("bid-reject" + System.currentTimeMillis());                                
                            myAgent.send(reject);
                        }
                    }

                    step = 4;
                    break;

                case 4:
                    // All bidders have dropped out simultaneously
                    if (amountOfBids == 0) {

                        // Stage switch to second-price sealed-bid auction
                        ACLMessage cfpSealedBid = new ACLMessage(ACLMessage.CFP);
                        amountOfRecipients = 0;

                        for (int i = 0; i < lowestBiddersLastRound.length; i++) {
                            if (lowestBiddersLastRound[i] != null) {
                                cfpSealedBid.addReceiver(lowestBiddersLastRound[i]);
                                amountOfRecipients++;
                            }
                        }

                        cfpSealedBid.setConversationId("second-price sealed bid");
                        cfpSealedBid.setReplyWith("cfpSealedBid" + System.currentTimeMillis());
                        myAgent.send(cfpSealedBid);

                        // Create a template for receiving sealed bids from bidders
                        mtSealedBid = MessageTemplate.and(
                            MessageTemplate.MatchConversationId("second-price sealed bid"),
                            MessageTemplate.MatchInReplyTo(cfpSealedBid.getReplyWith()));

                        // Process all sealed bids
                        while (amountOfRecipients > 0) {
                            ACLMessage replySealedBid = myAgent.receive(mtSealedBid);
                            if (replySealedBid != null) {
                                receivedReplies.put(replySealedBid.getSender(), Integer.parseInt(replySealedBid.getContent()));
                                amountOfRecipients = amountOfRecipients - 1;
                            } else {
                                block();
                            }
                        }

                        // Determine what the lowest bid and the second lowest bid is, and who the lowest bidder is.
                        Iterator<Map.Entry<AID, Integer>> iter3 = receivedReplies.entrySet().iterator();
                        int lowestBidUpdated = -1;
                        int secondLowestBid = -1;
                        while (iter3.hasNext()) {

                            Map.Entry<AID, Integer> item3 = iter3.next();

                            if (item3.getValue() != null) {

                                if (lowestBidUpdated == -1) {
                                    lowestBidUpdated = item3.getValue();
                                } else if (item3.getValue() <= lowestBidUpdated ) {
                                    secondLowestBid = lowestBidUpdated;
                                    lowestBidUpdated = item3.getValue();
                                } else if (item3.getValue() > lowestBidUpdated && (item3.getValue() < secondLowestBid || secondLowestBid == -1)) {
                                    secondLowestBid = item3.getValue();
                                }
                            }
                        }                        

                        // update lowestBidders array: Add the agent(s) back again that bid the lowest bid.
                        Iterator<Map.Entry<AID, Integer>> iter4 = receivedReplies.entrySet().iterator();
                        while (iter4.hasNext()) {
                            Map.Entry<AID, Integer> item4 = iter4.next();

                            if (item4.getValue() != null) {

                                if (item4.getValue() == lowestBidUpdated) {

                                    AID lowestBidderSealedBid = item4.getKey();

                                    for (int i = 0; i < lowestBidders.length; i++) {

                                        if (lowestBiddersLastRound[i] != null) {

                                            if (lowestBiddersLastRound[i].equals(lowestBidderSealedBid)) {
                                                lowestBidders[i] = lowestBidderSealedBid;
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        // Update lowest bid to be the second lowest bid from the second-price sealed bid auction
                        lowestBid = secondLowestBid;

                        // Progress with clearing and closing the auction
                        step = 5;
                    
                    // There's only one highest bidder remaining
                    } else if (amountOfBids == 1) {

                        // Progress with clearing and closing the auction
                        step = 5;
                    
                    // There are more than one highest bidder
                    } else {

                        roundNr++;
                        logger.log(Level.INFO, "Auctioneer: Round Nr." + roundNr + " - Do I hear $" + String.valueOf(lowestBid + increment) + "?\n");

                        // Update the selling price for the next round
                        lowestBid = lowestBid + increment;

                        // Start a new bidding round
                        step = 1;
                    }

                    break;
                case 5:

                    AID winner = null;
                    int amountOfPotentialWinners = 0;
                    for (int i = 0; i < lowestBidders.length; i++) {
                        if (lowestBidders[i] != null) {
                            amountOfPotentialWinners++;
                        }
                    }

                    logger.info("Amount of potential winners: " + amountOfPotentialWinners +"\n");

                    // If amount of lowest bidders = 1
                    if (amountOfPotentialWinners == 1) {
                        for (int i = 0; i < lowestBidders.length; i++) {
                            if (lowestBidders[i] != null) {
                                winner = lowestBidders[i];
                            }
                        }
                    // If amount of lowest bidders > 1, then pick one of them randomly to be the winner agent
                    } else if (amountOfPotentialWinners > 1) {
                        AID[] potentialWinnerAgents = new AID[amountOfPotentialWinners];
                        int j = 0;
                        for (int i = 0; i < lowestBidders.length; i++) {
                            if (lowestBidders[i] != null) {
                                potentialWinnerAgents[j] = lowestBidders[i];
                                j++;
                            }
                            if (j == (amountOfPotentialWinners)) {
                                break;
                            }
                        }

                        logger.log(Level.INFO, "Auctioneer: The following bidder agents have all bid the same amount: ");
                        for (int i = 0; i < amountOfPotentialWinners; i++) {
                            if (i < amountOfPotentialWinners - 2) {
                                logger.log(Level.INFO, potentialWinnerAgents[i].getName() + ", ");
                            } else if (i == amountOfPotentialWinners - 2) {
                                logger.log(Level.INFO, potentialWinnerAgents[i].getName() + ", and ");
                            } else {
                                logger.log(Level.INFO, potentialWinnerAgents[i].getName() + ".\n");
                            }
                        }

                        int randomWinnerIndex = ThreadLocalRandom.current().nextInt(0, amountOfPotentialWinners);
                        winner = potentialWinnerAgents[randomWinnerIndex];
                        logger.log(Level.INFO, "Auctioneer: The winner was arbitrarily chosen to be " + winner.getName() + "\n");
                    }

                    // Inform agents that the auction is over
                    // Create an ACLMessage that will be send to all bidders that didn't win
                    ACLMessage infoAuctionOver = new ACLMessage(ACLMessage.INFORM);
                    infoAuctionOver.setContent("Auction is over. The selling price of the auction is $" + lowestBid + ".");
                    infoAuctionOver.setConversationId("InformAuctionOver");

                    // Create an ACLMessage that will be send to the winner
                    ACLMessage infoWinner = new ACLMessage(ACLMessage.INFORM);
                    infoWinner.setContent("You won the auction with your bid $" + lowestBid + ".");
                    infoWinner.setConversationId("InformWinner");

                    for (int i = 0; i < bidderAgents.length; i++) {
                        if (bidderAgents[i] != null) {

                            if (winner.equals(bidderAgents[i])) {
                                infoWinner.addReceiver(bidderAgents[i]);
                            } else {
                                infoAuctionOver.addReceiver(bidderAgents[i]);
                            }
                        }
                    }

                    // Create a message for the evaluation agent, containing the information about who won & at what price.
                    ACLMessage auctionResult = new ACLMessage(ACLMessage.INFORM);
                    auctionResult.setContent(winner.getName() + "||" + lowestBid + "||" + problemComplexity + "||" + problemSize + "||" + startingPrice);
                    auctionResult.setConversationId("AuctionResult");
                    auctionResult.addReceiver(evaluationAgent);

                    // Send all ACLMessages
                    myAgent.send(infoAuctionOver);
                    myAgent.send(infoWinner);
                    myAgent.send(auctionResult);

                    logger.log(Level.INFO, "Auctioneer: Sold to the bidder " + winner.getName() + " for $" + lowestBid+"\n");

                    // End the AuctionPerformer behavior
                    step = 6;
                    break;
            }
        }

        private void printBidders (int amountOfBids) {

                    if (amountOfBids == 1) {  
                        logger.log(Level.INFO, "Auctioneer: Lowest bid so far: $" + lowestBid + " for agent ");
                        for (int i = 0; i < lowestBidders.length; i++) {
                            if (lowestBidders[i] != null) {
                                logger.log(Level.INFO, lowestBidders[i].getName() + ".\n");                       
                            }
                        }
                    } else if (amountOfBids > 1) {
                        logger.log(Level.INFO, "Auctioneer: Lowest bid so far: $" + lowestBid + " for agents ");
                        int count1 = 0;
                        for (int i = 0; i < lowestBidders.length; i++) {
                            if (lowestBidders[i] != null) {
                                count1++;                            
                            }
                        }
                        int count2 = 0;
                        for (int i = 0; i < lowestBidders.length; i++) {
                            if (lowestBidders[i] != null && count1 > count2 + 1) {
                                logger.log(Level.INFO, lowestBidders[i].getName() + ", ");
                                count2++;                            
                            } else if (lowestBidders[i] != null) {
                                logger.log(Level.INFO, lowestBidders[i].getName() + ".\n");
                                break;
                            } 
                        }
                    } else {
                        logger.log(Level.INFO, "Auctioneer: No bids received in this round. Hence, the mode of the auction will be changed to a second-price sealed bid auction.\n");
                    }
        }

        @Override
        public boolean done() {
            if (step == 6) {
                doDelete();
            }
            return (step == 6);
        }
    }
}
