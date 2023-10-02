package English;

import jade.core.Agent;
import jade.core.AID;
import jade.core.behaviours.Behaviour;
import jade.domain.DFService;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.domain.FIPAAgentManagement.ServiceDescription;
import jade.domain.FIPAException;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.MessageTemplate;

import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.ArrayList;
import java.util.List;

public class Bidder extends Agent implements BiddingBehavior {
    
    Logger logger = Logger.getLogger("AuctionLogger");

    @Override
    protected void setup() {

        // Register bidder in the yellow pages
        DFAgentDescription dfd = new DFAgentDescription();
        dfd.setName(getAID());
        ServiceDescription sd = new ServiceDescription();
        sd.setName("Bidder");
        sd.setType("Normal");
        dfd.addServices(sd);

        try {
            DFService.register(this, dfd);
        } catch (FIPAException e) {
            e.printStackTrace();
        }

        // Add bidder behavior
        addBehaviour(new BidderBehavior());
    }   

    @Override
    protected void takeDown() {

        try {
            DFService.deregister(this);
        } catch (FIPAException e) {
            e.printStackTrace();
        }
        logger.log(Level.INFO, "Bidder " + getAID().getName() + " terminating.\n");
        doDelete();
    }

    private class BidderBehavior extends Behaviour {

        private AID evaluationAgent;

        private Integer problemSize;
        private String problemComplexity;
        private Double trueTaskCostliness;
        private Double estimationTaskCostliness;
        private String itemName;
        private Long[] initiallyEstimatedBidderDistribution;
        private Double averageInitiallyEstimatedBidderDistribution;
        private Long[] currentEstimationBidderDistribution;
        private Double averageCurrentEstimationBidderDistribution;
        private Double correctionTerm;
        private List<Double> correctionTermPerAuctionRound = new ArrayList<>();
        private Double avgCorrectionTerm;

        private Integer amountOfBidders;
        private Integer amountOfActiveBidders;

        private Long itemPrice;
        private Long itemPriceLastRound;
        private Long commonCost;
        private Long initialReservationPrice;
        private Long reservationPrice;
        private Integer roundNr;

        private Long executionCost;
        public Double alpha = Configuration.alpha;
        private Double hardwareCoefficient;
        private Double beta = Configuration.beta;
        private Double tcAdjustmentCoefficient = beta * 2;

        @Override
        public void action() { 

            // Create a message template for the message containing the information about the computational task
            MessageTemplate mtINF = MessageTemplate.MatchPerformative(ACLMessage.INFORM);
            ACLMessage msgINF = myAgent.receive(mtINF);

            // If said message was received, then process it the following way
            if (msgINF != null && msgINF.getConversationId().equals("information computational task")) {

                // Setup cost function
                parseContentINF(msgINF.getContent());
                hardwareCoefficient = determineHardwareCoefficient(alpha);
                estimationTaskCostliness = estimateTaskCostliness(trueTaskCostliness, beta);
                commonCost = calculateCommonCost(problemSize, problemComplexity);

                // Calculate the (unadjusted) initial reservation price
                initialReservationPrice = calculateInitialReservationPrice(commonCost, hardwareCoefficient, estimationTaskCostliness);
                logger.log(Level.INFO, getAID().getName() + ": I am ready. (My initial reservation price is $" + initialReservationPrice + ", my hardware coefficient is " + hardwareCoefficient +", and my initial task costliness estimate is " + estimationTaskCostliness + ").\n");

                // Create the distributions that are used in the correction term
                estimateInitialBidderDistribution(commonCost, estimationTaskCostliness, amountOfBidders);
                estimateFirstRoundBidderDistribution(commonCost, alpha, estimationTaskCostliness, tcAdjustmentCoefficient, amountOfBidders);

            } else {
                block();
            }

            // Create a message template for call for proposals by the auctioneer
            MessageTemplate mtCFP = MessageTemplate.MatchPerformative(ACLMessage.CFP);
            ACLMessage msgCFP = myAgent.receive(mtCFP);

            // A normal auction round
            if (msgCFP != null && msgCFP.getConversationId().equals("cfp english auction")) {

                parseContentCFP(msgCFP.getContent());

                // Adjust distribution and reservation price based on the current state of the auction
                estimateCurrentBidderDistribution(itemPrice, amountOfActiveBidders, roundNr);
                correctionTerm = calculateDiscrepancyBetweenDistributions(averageCurrentEstimationBidderDistribution, averageInitiallyEstimatedBidderDistribution);
                correctionTermPerAuctionRound.add(correctionTerm);
                reservationPrice = adjustReservationPrice(commonCost, hardwareCoefficient, estimationTaskCostliness, tcAdjustmentCoefficient, correctionTerm);

                // Create a reply to the cfp.
                ACLMessage reply = msgCFP.createReply();
                Long bid;

                // If the item price is below the reservation price, then bid
                if (itemPrice >= reservationPrice) {

                    bid = itemPrice;
                    reply.setPerformative(ACLMessage.PROPOSE);
                    reply.setContent(String.valueOf(bid));

                } else {
                    
                    reply.setPerformative(ACLMessage.REFUSE);
                }
                
                myAgent.send(reply);
            
            // If a stage switch to a second-price sealed-bid auction was conducted 
            } else if (msgCFP != null && msgCFP.getConversationId().equals("second-price sealed bid")) {

                // The assumption made about all bidders dropping out was correct. Hence, the old reservation price is still relevant - no adjustments have to be made
                ACLMessage reply = msgCFP.createReply();
                reply.setPerformative(ACLMessage.PROPOSE);
                reply.setContent(String.valueOf(reservationPrice));
                myAgent.send(reply);
                logger.log(Level.INFO, reply.getSender().getName() + ": My sealed bid is $" + reservationPrice + "!\n");
            } else {
                block();
            }

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

                // Send a message to the evaluation agent containing all the relevant bidder data, such as his reservation price, his execution cost, and his average correction term
                executionCost = calculateExecutionCost(commonCost, hardwareCoefficient, trueTaskCostliness);
                avgCorrectionTerm = calculateAvgCorrectionTerm(correctionTermPerAuctionRound);
                ACLMessage bidderInformation = new ACLMessage(ACLMessage.INFORM);
                bidderInformation.setConversationId("BidderInformation");
                bidderInformation.addReceiver(evaluationAgent);
                bidderInformation.setContent(myAgent.getName() + "||" + reservationPrice + "||" + executionCost + "||" + avgCorrectionTerm);
                myAgent.send(bidderInformation);
                
                doDelete();

            } else {
                block();
            }
        }

        private void parseContentINF(String content) {

            String[] split = content.split("\\|\\|");
            
            problemSize = Integer.parseInt(split[0]);
            problemComplexity = split[1];
            trueTaskCostliness = Double.parseDouble(split[2]);
            amountOfBidders = Integer.parseInt(split[3]);
        }

        private void estimateInitialBidderDistribution(long cc, Double tc, int ab) {
            
            // Setup
            initiallyEstimatedBidderDistribution = new Long[ab-1];

            // A uniform distribution for the hardware coefficients is assumed
            Double min = 1 - alpha;
            Double max = 1 + alpha;
            Double range = max - min;
            Double sizeOfIncrement;

            if (ab > 2 ){
                sizeOfIncrement = range / (double) (ab-2);
            } else {
                sizeOfIncrement = alpha;
            }

            long sum = 0;

            for (int i = 0; i < (ab-1); i++) {

                long estimate = (int) Math.ceil( cc * tc * (max - i * sizeOfIncrement));
                initiallyEstimatedBidderDistribution[i] = estimate;
                sum = sum + estimate;

            }

            // Compute the average.
            averageInitiallyEstimatedBidderDistribution = (double) sum / (double) (ab-1);
            averageInitiallyEstimatedBidderDistribution = Double.parseDouble(decimalFormat.format(averageInitiallyEstimatedBidderDistribution));
        }

        private void parseContentCFP(String content) {

            String[] split = content.split("\\|\\|");

            itemName = split[0];
            itemPrice = Long.parseLong(split[1]);
            amountOfActiveBidders = Integer.parseInt(split[2]);
            roundNr = Integer.parseInt(split[3]);

        }

        private void estimateFirstRoundBidderDistribution(long cc, Double a, Double etc, Double b, int ab) {

            // Setup
            currentEstimationBidderDistribution = new Long[ab-1];

            // Worst case estimate: Worst hardware coefficient possible (1 + alpha) & worst task costliness that is theoretically possible (agents can be off by up to the value of the variable "tcAdjustmentCoefficient").
            long firstRoundWorstCaseEstimate = (int) Math.ceil(cc * (1 + a) * (etc + b));
            itemPriceLastRound = firstRoundWorstCaseEstimate;

            for (int i = 0; i < (ab-1); i++) {
                currentEstimationBidderDistribution[i] = firstRoundWorstCaseEstimate;
            }
        }

        private void estimateCurrentBidderDistribution(long cp, int aab, int rn) {
            
            // Update the current bidder distribution based on the observed bidding behavior of other bidders
            if (rn > 1 && aab > 0) {
                int startLoop = (amountOfBidders-1) - (aab-1);
                for (int i = startLoop; i < amountOfBidders-1; i++) {
                        currentEstimationBidderDistribution[i] = itemPriceLastRound;
                } 
            }

            // Compute the average of the distribution
            long sum = 0; 
            for (int i = 0; i < (amountOfBidders-1); i++) {
                sum = sum + currentEstimationBidderDistribution[i];
            }
            averageCurrentEstimationBidderDistribution = (double) sum / (double) (amountOfBidders - 1);
            averageCurrentEstimationBidderDistribution = Double.parseDouble(decimalFormat.format(averageCurrentEstimationBidderDistribution));

            itemPriceLastRound = cp;
        }

        @Override
        public boolean done() {
            return false;
        }
    }
}