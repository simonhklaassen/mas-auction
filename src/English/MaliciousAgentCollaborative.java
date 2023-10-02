package English;

import jade.core.Agent;
import jade.core.AID;
import jade.core.behaviours.Behaviour;
import jade.core.behaviours.OneShotBehaviour;
import jade.domain.DFService;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.domain.FIPAAgentManagement.ServiceDescription;
import jade.domain.FIPAException;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.MessageTemplate;

import java.text.DecimalFormat;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.ArrayList;
import java.util.List;


public class MaliciousAgentCollaborative extends Agent implements BiddingBehavior {

    Logger logger = Logger.getLogger("AuctionLogger");
    DecimalFormat decimalFormat = BiddingBehavior.decimalFormat;

    private String itemName;
    private Integer roundNr;
    private Long itemPrice;
    private Long itemPriceLastRound;

    private Integer amountOfBidders = 0;
    private Integer amountOfActiveBidders;
    private int amountOfCollusiveMaliciousBidderAgents;
    private AID[] collusiveMaliciousBidderAgents;

    private Integer problemSize;
    private String problemComplexity;
    private Long commonCost;
    public Double alpha = Configuration.alpha;
    private Double hardwareCoefficient;
    private Double trueTaskCostliness;
    public Double beta = Configuration.beta;
    private Double estimationTaskCostliness;
    private Double estimationTaskCostlinessRing;
    private Long reservationPrice;

    private Double betaRing; 
    private Double tcAdjustmentCoefficient;
    private boolean isBidding = true;

    private MessageTemplate mtPrivateInformation;
    private Double[] taskCostlinessEstimates;
    private Map<String, Double> hardwareCoefficients = new HashMap<>();
    private int counterRepliesPIMessage;
    private String otherAgentName;
    private Double hardwareCoefficientOtherAgent;
    private Double estimationTaskCostlinessOtherAgent;

    private Long[] initiallyEstimatedBidderDistribution;
    private Double averageInitiallyEstimatedBidderDistribution;
    private Long[] currentEstimationBidderDistribution;
    private Double averageCurrentEstimationBidderDistribution;
    private Double correctionTerm;
    private List<Double> correctionTermPerAuctionRound = new ArrayList<>();
    private Double avgCorrectionTerm;

    private AID evaluationAgent;
    private Long executionCost;

    private boolean receivedINFAuctioneer = false;
    private boolean processedINFAuctioneer = false;

    @Override
    protected void setup() {

        // Registration in the yellow pages
        DFAgentDescription dfd = new DFAgentDescription();
        dfd.setName(getAID());
        ServiceDescription sd = new ServiceDescription();
        sd.setName("Bidder");
        sd.setType("Malicious-Collusive");
        dfd.addServices(sd);
        try {
            DFService.register(this, dfd);
        } catch (FIPAException e) {
            e.printStackTrace();
        }

        // Behavior to identify other collaborative malicious bidders
        addBehaviour(new OneShotBehaviour() {

            @Override
            public void action() { 

                DFAgentDescription templateBidder = new DFAgentDescription();
                ServiceDescription sdBidder = new ServiceDescription();
                sdBidder.setName("Bidder");
                sdBidder.setType("Malicious-Collusive");
                templateBidder.addServices(sdBidder);
                block(50);

                try {
                    DFAgentDescription[] result = DFService.search(myAgent, templateBidder);
                    collusiveMaliciousBidderAgents = new AID[result.length-1];
                    amountOfCollusiveMaliciousBidderAgents = result.length - 1;

                    int j = 0;
                    int i;
                    for (i = 0; i < result.length; i++) {
                        if (!result[i].getName().equals(dfd.getName())) {
                            collusiveMaliciousBidderAgents[j] = result[i].getName();
                            j++;
                        }
                    }
                    if (result.length == 0) {
                        logger.log(Level.INFO, "No registered bidder could be found.\n");
                    }
                } catch (FIPAException e) {
                    e.printStackTrace();
                }
            }
        });

        // Receive information about the computational task
        addBehaviour(new Behaviour() {

            @Override
            public void action() { 

                while (receivedINFAuctioneer != true) {

                    // Create a message template for the message containing the information about the computational task
                    MessageTemplate mtINF = MessageTemplate.MatchPerformative(ACLMessage.INFORM);
                    ACLMessage msgINF = myAgent.receive(mtINF);
                    
                    // If said message was received, then process it the following way
                    if (msgINF != null && msgINF.getConversationId().equals("information computational task")) {

                        receivedINFAuctioneer = true;

                        // Setup cost function
                        parseContentTaskINF(msgINF.getContent());
                        hardwareCoefficient = determineHardwareCoefficientUnrounded(alpha);
                        estimationTaskCostliness = estimateTaskCostliness(trueTaskCostliness, beta);
                        logger.log(Level.INFO, getAID().getName() + ": I am ready. (My hardware coefficient is " + decimalFormat.format(hardwareCoefficient) +", and my initial task costliness estimate is " + estimationTaskCostliness + ").\n");
                        
                        // Exchange task costliness estimate with other malicious agents in the ring
                        ACLMessage privateInformation = new ACLMessage(ACLMessage.INFORM);
                        privateInformation.setConversationId("SharingTaskCostlinessEstimate");
                        for (int i = 0; i < amountOfCollusiveMaliciousBidderAgents; i++) {
                            privateInformation.addReceiver(collusiveMaliciousBidderAgents[i]);
                        }
                        privateInformation.setContent(myAgent.getName() + "||" + estimationTaskCostliness + "||" + hardwareCoefficient);
                        myAgent.send(privateInformation);

                        mtPrivateInformation = 
                            MessageTemplate.MatchConversationId("SharingTaskCostlinessEstimate");

                        taskCostlinessEstimates = new Double[amountOfCollusiveMaliciousBidderAgents];
                        hardwareCoefficients = new HashMap<>();
                        counterRepliesPIMessage = 0;

                        while (counterRepliesPIMessage < amountOfCollusiveMaliciousBidderAgents) {
                            ACLMessage replyPIMessage = myAgent.receive(mtPrivateInformation);
                            if (replyPIMessage != null) {
                                parseContentSharingPrivateINF(replyPIMessage.getContent());
                                taskCostlinessEstimates[counterRepliesPIMessage] = estimationTaskCostlinessOtherAgent;
                                hardwareCoefficients.put(otherAgentName, hardwareCoefficientOtherAgent); 
                                counterRepliesPIMessage++;
                            } else {
                                block();
                            }
                        }

                        // Based on the estimates of others, create a new task costliness estimate and a new adjustment parameter (replace beta value).
                        estimationTaskCostlinessRing = estimateTaskCostlinessRing(taskCostlinessEstimates, estimationTaskCostliness, amountOfCollusiveMaliciousBidderAgents);
                        betaRing = calculateRingBeta(beta, amountOfCollusiveMaliciousBidderAgents);
                        
                        // Determine the agent that will bid for the ring, based on their hardware coefficient
                        Iterator<Map.Entry<String, Double>> iter = hardwareCoefficients.entrySet().iterator();
                        while (iter.hasNext()) {
                            Map.Entry<String, Double> item = iter.next();
                            if (item.getValue() < hardwareCoefficient) {
                                isBidding = false;
                                processedINFAuctioneer = true;
                                break;
                            }
                        }

                        // Do the full agent setup for the malicious bidder agent that will represent the ring in the auction
                        if (isBidding == true) {

                            hardwareCoefficient = Double.parseDouble(decimalFormat.format(hardwareCoefficient));
                            commonCost = calculateCommonCost(problemSize, problemComplexity);
                            logger.info(myAgent.getName() + ": I will be bidding for the ring. The ring estimates the task costliness to be: " + estimationTaskCostlinessRing + " and beta = " + betaRing + ". My hardware coefficient is: " + hardwareCoefficient + ".\n");

                            // Create an estimated distribution of other bidders.
                            estimateInitialBidderDistribution(commonCost, estimationTaskCostlinessRing, amountOfBidders, amountOfCollusiveMaliciousBidderAgents);
                            amountOfActiveBidders = amountOfBidders;
                            tcAdjustmentCoefficient = betaRing * 2;
                            estimateFirstRoundBidderDistribution(commonCost, alpha, estimationTaskCostlinessRing, tcAdjustmentCoefficient, amountOfActiveBidders, amountOfCollusiveMaliciousBidderAgents);

                            processedINFAuctioneer = true;
                        }

                    } else {
                        block();
                    }
                }

            }

            public boolean done() {
                return processedINFAuctioneer;
            }

        });

        // Add the malicious bidder behavior
        addBehaviour(new MaliciousCollusiveBiddingBehavior());
    }

    @Override
    protected void takeDown() {
        try {
            DFService.deregister(this);
        } catch (FIPAException e) {
            e.printStackTrace();
        }

        logger.log(Level.INFO, "Malicious Agent " + getAID().getName() + " terminating.\n");
        doDelete();
    }

        private void parseContentTaskINF(String content) {

            String[] split = content.split("\\|\\|");
            
            problemSize = Integer.parseInt(split[0]);
            problemComplexity = split[1];
            trueTaskCostliness = Double.parseDouble(split[2]);
            amountOfBidders = Integer.parseInt(split[3]);
        }

        private void parseContentSharingPrivateINF(String content) {
            String[] split = content.split("\\|\\|");
            
            otherAgentName = split[0];
            estimationTaskCostlinessOtherAgent = Double.parseDouble(split[1]);
            hardwareCoefficientOtherAgent = Double.parseDouble(split[2]);
        }

        private Double estimateTaskCostlinessRing(Double[] tce, Double etc, int aocmba) {

            Double sum = etc;
            for (int i = 0; i < aocmba; i++) {
                sum = sum + tce[i];
            }
            Double etcr = sum / (double) (aocmba + 1);
            etcr = Double.parseDouble(decimalFormat.format(etcr));

            return etcr;
        }

        private Double calculateRingBeta(Double b, int aocmba) {

            Double standardError = b / Math.sqrt(aocmba + 1);
            standardError = Double.parseDouble(decimalFormat.format(standardError));

            return standardError;
        }

        private void estimateInitialBidderDistribution(long cc, Double tc, int ab, int aocmba) {
            
            // Setup
            initiallyEstimatedBidderDistribution = new Long[ab-aocmba-1];

            // A uniform distribution for the hardware coefficients is assumed
            Double min = 1 - alpha;
            Double max = 1 + alpha;
            Double range = max - min;
            Double sizeOfIncrement;

            if ((ab - aocmba) > 2 ) {
                sizeOfIncrement = range / (double) (ab-aocmba-2);
            } else {
                sizeOfIncrement = alpha;
            }

            long sum = 0;

            for (int i = 0; i < (ab-aocmba-1); i++) {

                long estimate = (int) Math.ceil( cc * tc * (max - i * sizeOfIncrement));
                initiallyEstimatedBidderDistribution[i] = estimate;
                sum = sum + estimate;

            }

            // Compute the average.
            averageInitiallyEstimatedBidderDistribution = (double) sum / (double) (ab-aocmba-1);
            averageInitiallyEstimatedBidderDistribution = Double.parseDouble(decimalFormat.format(averageInitiallyEstimatedBidderDistribution));
        }

        private void estimateFirstRoundBidderDistribution(long cc, Double a, Double etc, Double b, int ab, int aocmba) {

            // Setup
            currentEstimationBidderDistribution = new Long[ab-aocmba-1];

            // Worst case estimate: Worst hardware coefficient possible (1 + alpha) & worst task costliness that is theoretically possible (agents can be off by up to the value of the variable "tcAdjustmentCoefficient").
            long firstRoundWorstCaseEstimate = (int) Math.ceil(cc * (1 + a) * (etc + b));
            itemPriceLastRound = firstRoundWorstCaseEstimate;

            for (int i = 0; i < (ab-aocmba-1); i++) {
                currentEstimationBidderDistribution[i] = firstRoundWorstCaseEstimate;
            }  
        }

    private class MaliciousCollusiveBiddingBehavior extends Behaviour {

        @Override
        public void action() { 

            // Generate a new message template for CFPs.
            MessageTemplate mtCFP = MessageTemplate.MatchPerformative(ACLMessage.CFP);
            ACLMessage msgCFP = myAgent.receive(mtCFP);

            // A normal auction round
            if (msgCFP != null && msgCFP.getConversationId().equals("cfp english auction")) {
                
                // If the malicious bidder doesn't bid actively for the ring in the auction, then he will drop out immediately
                if (isBidding == false) {
                    ACLMessage reply = msgCFP.createReply();
                    reply.setPerformative(ACLMessage.REFUSE);
                    myAgent.send(reply);

                // If the malicious bidder represents the ring in the auction, he behaves like a normal bidder
                } else if (isBidding == true) {

                    // Store contents of cfp message.
                    parseContentCFP(msgCFP.getContent());

                    // Adjust distribution and reservation price based on the current state of the auction
                    estimateCurrentBidderDistribution(itemPrice, amountOfBidders, amountOfActiveBidders, amountOfCollusiveMaliciousBidderAgents, roundNr);
                    correctionTerm = calculateDiscrepancyBetweenDistributions(averageCurrentEstimationBidderDistribution, averageInitiallyEstimatedBidderDistribution);
                    correctionTermPerAuctionRound.add(correctionTerm);
                    reservationPrice = adjustReservationPrice(commonCost, hardwareCoefficient, estimationTaskCostlinessRing, tcAdjustmentCoefficient, correctionTerm);

                    // Create a reply to the cfp.
                    ACLMessage reply = msgCFP.createReply();
                    long bid;

                    // If the item price is below the reservation price, then bid
                    if (itemPrice >= reservationPrice) {

                        bid = itemPrice;
                        reply.setPerformative(ACLMessage.PROPOSE);
                        reply.setContent(String.valueOf(bid));

                    } else {

                        reply.setPerformative(ACLMessage.REFUSE);

                    }

                    myAgent.send(reply);
                }

            // If a stage switch to a second-price sealed-bid auction was conducted 
            } else if (msgCFP != null && msgCFP.getConversationId().equals("second-price sealed bid")) { //&& processedINFAuctioneer == true

                // The assumption made about all bidders dropping out was correct. Hence, the old reservation price is still relevant - no adjustments have to be made
                ACLMessage reply = msgCFP.createReply();
                reply.setPerformative(ACLMessage.PROPOSE);
                reply.setContent(String.valueOf(reservationPrice));
                myAgent.send(reply);
                logger.log(Level.INFO, reply.getSender().getName() + ": My sealed bid is $" + reservationPrice + "!\n");
            } else {
                block();
            }

            // Create a message template for the message containing the information about the computational task
            MessageTemplate mtINF = MessageTemplate.MatchPerformative(ACLMessage.INFORM);
            ACLMessage msgINF = myAgent.receive(mtINF);

            // Once the auction was closed by the auctioneer
            if (msgINF != null && (msgINF.getConversationId().equals("InformAuctionOver") || msgINF.getConversationId().equals("InformWinner"))) {
                
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

                ACLMessage bidderInformation = new ACLMessage(ACLMessage.INFORM);
                bidderInformation.setConversationId("BidderInformation");
                bidderInformation.addReceiver(evaluationAgent);

                if (isBidding == true) {

                    // Send a message to the evaluation agent containing all the relevant bidder data, such as his reservation price, his execution cost, and his average correction term
                    executionCost = calculateExecutionCost(commonCost, hardwareCoefficient, trueTaskCostliness);
                    avgCorrectionTerm = calculateAvgCorrectionTerm(correctionTermPerAuctionRound);
                    int maliciousBidder = 1;
                    bidderInformation.setContent(myAgent.getName() + "||" + reservationPrice + "||" + executionCost + "||" + avgCorrectionTerm + "||" + maliciousBidder);
                
                } else {

                    executionCost = Long.MAX_VALUE;
                    reservationPrice = Long.MAX_VALUE;
                    bidderInformation.setContent(myAgent.getName() + "||" + reservationPrice + "||" + executionCost);

                }

                myAgent.send(bidderInformation);

                doDelete();

            } else {
                block();
            }
        }

        private void parseContentCFP(String content) {
            String[] split = content.split("\\|\\|");

            itemName = split[0];
            itemPrice = Long.parseLong(split[1]);
            amountOfActiveBidders = Integer.parseInt(split[2]);
            roundNr = Integer.parseInt(split[3]);

        }

        private void estimateCurrentBidderDistribution(long cp, int ab, int aab, int aocmba, int rn) {

            // Update the current bidder distribution based on the observed bidding behavior of other bidders
            if (rn > 1 && aab > 0) {
                int startLoop = (ab-aocmba-1) - (aab-1);
                for (int i = startLoop; i < (ab-aocmba-1); i++) {
                        currentEstimationBidderDistribution[i] = itemPriceLastRound;
                } 
            }
            // Compute the average of the distribution
            long sum = 0; 
            for (int i = 0; i < (ab-aocmba-1); i++) {
                sum = sum + currentEstimationBidderDistribution[i];
            }
            averageCurrentEstimationBidderDistribution = (double) sum / (double) (ab - aocmba - 1);
            averageCurrentEstimationBidderDistribution = Double.parseDouble(decimalFormat.format(averageCurrentEstimationBidderDistribution));

            itemPriceLastRound = cp;
        }

        @Override
        public boolean done() {
            return false;
        }

    }
}

