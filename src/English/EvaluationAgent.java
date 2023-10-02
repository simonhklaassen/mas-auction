package English;

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
import java.util.logging.Logger;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;

import org.json.JSONObject;
import java.io.FileWriter;

public class EvaluationAgent extends Agent {

    private Integer amountOfBidders;
    private int experimentRound;
    private String storageDirectoryLogFile;

    Logger logger = Logger.getLogger("AuctionLogger");

    JSONObject auctionResults = new JSONObject();

    @Override
    protected void setup() {  

        Object[] args = getArguments();

        if (args != null && args.length > 0) {

            // Setup
            experimentRound = Integer.parseInt((String) args[0]);
            storageDirectoryLogFile = (String) args[1];
            auctionResults.put("experiment_round", experimentRound + 1);

            // Register the evaluation agent in the yellow pages
            DFAgentDescription dfd = new DFAgentDescription();
            dfd.setName(getAID());
            ServiceDescription sd = new ServiceDescription();
            sd.setName("Evaluation-Agent");
            sd.setType("-");
            dfd.addServices(sd);
            try {
                DFService.register(this, dfd);
            } catch (FIPAException e) {
                e.printStackTrace();
            }

            logger.log(Level.INFO, "Evaluation agent: I am ready.\n");
        
            // Add behavior that finds out how many bidders are participating
            addBehaviour(new OneShotBehaviour() {

                @Override
                public void action() {

                    // Look up all bidders in the yellow pages
                    DFAgentDescription template = new DFAgentDescription();
                    ServiceDescription sd = new ServiceDescription();
                    sd.setName("Bidder");
                    template.addServices(sd);

                    try {
                        DFAgentDescription[] result = DFService.search(myAgent, template);
                        amountOfBidders = result.length;
                    } catch (FIPAException e) {
                        e.printStackTrace();
                    }

                    }
                });

            // Add core behavior of evaluation agent: Gathering the auction results and calculating the efficiency and optimality
            addBehaviour(new Evaluation());
        }
    }

    @Override
    protected void takeDown() {
        try {
            DFService.deregister(this);
        } catch (FIPAException e) {
            e.printStackTrace();
        }

        logger.log(Level.INFO, "Evaluation agent " + getAID().getName() + " terminating.\n");
        doDelete();
        // Terminate the java program
        System.exit(0);
    }

    private class Evaluation extends Behaviour {

        private Integer counter = 0;

        private String problemComplexity;
        private int problemSize;

        private Integer decimalPlacesRounding = 3;
        DecimalFormat decimalFormat = new DecimalFormat("0." + "0".repeat(decimalPlacesRounding));

        private String winner;
        private int winnerIsMalicious = 0;
        private Long startingPrice;
        private Long sellingPrice;
        private Long executionCostWinner;
        private Long minimalExecutionCost = Long.MAX_VALUE;
        private Long lowestReservationPrice = Long.MAX_VALUE;

        private Double correctionTermMaliciousRingBidder = 0.0;
        private List<Double> avgCorrectionTermNormalBidders = new ArrayList<>();
        private Double avgCorrectionTermNormalBiddersFinal;

        private Double optimality;
        private Double efficiency;

        private Double xCoordinateParetoFrontier;
        private Double yCoordinateParetoFrontier;

        private boolean receivedINFAuctioneer = false;
        private boolean receivedAllINFBidders = false;

        @Override
        public void action() { 

            // Receive message from the auctioneer, containing the inormation who won the auction and at what price
            while (receivedINFAuctioneer != true) {

                MessageTemplate mtINF = MessageTemplate.MatchPerformative(ACLMessage.INFORM);
                ACLMessage msgINF = myAgent.receive(mtINF);

                if (msgINF != null && msgINF.getConversationId().equals("AuctionResult")) {
                    receivedINFAuctioneer = true;
                    parseContentINFAuctioneer(msgINF.getContent());
                } else {
                    block();
                }
            }

            while (receivedAllINFBidders != true) {

                MessageTemplate mtINF = MessageTemplate.MatchPerformative(ACLMessage.INFORM);
                ACLMessage msgINF = myAgent.receive(mtINF);

                // Receive messages from bidders containing their reservation prices and what their theoretical execution costs would have been
                if (msgINF != null && msgINF.getConversationId().equals("BidderInformation")) {

                    parseContentINFBidder(msgINF.getContent());
                    counter++;
                    // logger.info(lowestReservationPrice + ".\n");

                } else {
                    block();
                }

                // Calculate optimality, efficiency, and the coordinates of the Pareto frontier. Store them in a .json file
                if (counter.equals(amountOfBidders)) {

                    receivedAllINFBidders = true;

                    // Calculations
                    optimality = calculateOptimality();
                    efficiency = calculateEfficiency();
                    xCoordinateParetoFrontier = calculateXCoordinateParetoFrontier(startingPrice, sellingPrice, executionCostWinner, minimalExecutionCost);
                    yCoordinateParetoFrontier = calculateYCoordinateParetoFrontier(startingPrice, sellingPrice, minimalExecutionCost);

                    // Store the results in a .json file
                    avgCorrectionTermNormalBiddersFinal = calculateAvgCorrectionTerm(avgCorrectionTermNormalBidders);
                    auctionResults.put("problem_complexity", problemComplexity);
                    auctionResults.put("problem_size", problemSize);
                    auctionResults.put("avg_correction_term_normal_bidders", avgCorrectionTermNormalBiddersFinal);
                    auctionResults.put("optimality", optimality);
                    auctionResults.put("efficiency", efficiency);
                    auctionResults.put("x_coordinate_pareto_frontier", xCoordinateParetoFrontier);
                    auctionResults.put("y_coordinate_pareto_frontier", yCoordinateParetoFrontier);
                    if (correctionTermMaliciousRingBidder != 0.0) {
                        auctionResults.put("avg_correction_term_malicious_bidder", correctionTermMaliciousRingBidder);
                         if (winnerIsMalicious == 1) {
                            auctionResults.put("malicious", 1);
                         } else {
                            auctionResults.put("malicious", 0);
                         }
                    }

                    // Create the .json file.
                    try (FileWriter file = new FileWriter(storageDirectoryLogFile+"experiment" + (experimentRound + 1) + ".json")) {
                        file.write(auctionResults.toString());
                        file.flush();
                    } catch (IOException e) {
                        e.printStackTrace();
                    }

                    doDelete();
                }
            }
        
        }

        private Double calculateOptimality () {
            
            return Double.parseDouble(decimalFormat.format(((double) sellingPrice - (double) lowestReservationPrice) / (double) lowestReservationPrice));
        }

        private Double calculateEfficiency () {

            return Double.parseDouble(decimalFormat.format(((double) executionCostWinner - (double) minimalExecutionCost) / (double) minimalExecutionCost));
        }

        private Double calculateAvgCorrectionTerm(List<Double> ctpar) {

            int length = ctpar.size();
            double sum = 0;
            for (int i = 0; i < length; i++) {
                sum = sum + ctpar.get(i);
            }
            Double avgCorrectionTerm = sum / length;
            avgCorrectionTerm = Double.parseDouble(decimalFormat.format(avgCorrectionTerm));
    
            return avgCorrectionTerm;
        }

        private Double calculateXCoordinateParetoFrontier(long startP, long sellingP, long ecw, long mec) {

            double x = Double.parseDouble(decimalFormat.format(((double) (sellingP - ecw) / (startP - mec))));

            return x;
        }

        private Double calculateYCoordinateParetoFrontier(long startP, long sellingP, long mec) {

            double y = Double.parseDouble(decimalFormat.format(((double) (startP - sellingP) / (startP - mec))));

            return y;
        }

        private void parseContentINFAuctioneer (String content) {

            String[] split = content.split("\\|\\|");
            
            winner = split[0];
            sellingPrice = Long.parseLong(split[1]);
            problemComplexity = split[2];
            problemSize = Integer.parseInt(split[3]);
            startingPrice = Long.parseLong(split[4]);

        }

        private void parseContentINFBidder (String content) {

            String[] split = content.split("\\|\\|");

            String bidderName = split[0];
            Long reservationPrice = Long.parseLong(split[1]);
            Long executionCost= Long.parseLong(split[2]);

            if (split.length == 4 || split.length == 5) {

                Double avgCorrectionTerm = Double.parseDouble(split[3]);

                if (split.length == 4) {
                    avgCorrectionTermNormalBidders.add(avgCorrectionTerm);
                } else {
                    correctionTermMaliciousRingBidder = avgCorrectionTerm;
                }

                if (winner.equals(bidderName)) {
                    executionCostWinner = executionCost;
                    
                    if (split.length == 5) {
                        winnerIsMalicious = 1;
                    }
                }
            }

            // Check whether the reservation price is lower than the currently lowest reservation price
            if (reservationPrice < lowestReservationPrice) {
                lowestReservationPrice = reservationPrice;
            }

            // Check whether the execution cost is lower than the currently lowest execution cost
            if (executionCost < minimalExecutionCost) {
                minimalExecutionCost = executionCost;
            }
        }

        @Override
        public boolean done() {
            return false;
        }
    }
}