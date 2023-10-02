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

public class MaliciousAgentSolo extends Agent {
    
    Logger logger = Logger.getLogger("AuctionLogger");

    @Override
    protected void setup() {

        // Registration in the yellow pages
        DFAgentDescription dfd = new DFAgentDescription();
        dfd.setName(getAID());
        ServiceDescription sd = new ServiceDescription();
        sd.setName("Bidder");
        sd.setType("Malicious-Solo");
        dfd.addServices(sd);
        try {
            DFService.register(this, dfd);
        } catch (FIPAException e) {
            e.printStackTrace();
        }

        // Add Bidder Behavior
        addBehaviour(new MaliciousBiddingBehavior());
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

    private class MaliciousBiddingBehavior extends Behaviour {

        private Long reservationPrice;
        private Long executionCost;
        private AID evaluationAgent;

    
        @Override
        public void action() { 

            // Create a message template for the message containing the information about the computational task
            MessageTemplate mtINF = MessageTemplate.MatchPerformative(ACLMessage.INFORM);
            ACLMessage msgINF = myAgent.receive(mtINF);

            // If said message was received, then process it the following way
            if (msgINF != null && msgINF.getConversationId().equals("information computational task")) {

                // The malicious agent doesn't have any interest in executing the task (e.g. because he doesn't have any free capacity). As a consequence, his reservation price and exeuction cost are infinitely high.
                reservationPrice = Long.MAX_VALUE;
                executionCost = Long.MAX_VALUE;

                logger.log(Level.INFO, getAID().getName() + ": I am ready. (My reservation price is infinitely high).\n");

            } else {
                block();
            }

            // Create a message template for call for proposals by the auctioneer
            MessageTemplate mtCFP = MessageTemplate.MatchPerformative(ACLMessage.CFP);
            ACLMessage msgCFP = myAgent.receive(mtCFP);

            // If the bidder agents received a cfp
            if (msgCFP != null && msgCFP.getConversationId().equals("cfp english auction")) {
                
                // Because the malicious agent will always reject to bid, he doesn't have to reason at all: He'll just reply with a refusal
                ACLMessage reply = msgCFP.createReply();
                reply.setPerformative(ACLMessage.REFUSE);
                myAgent.send(reply);

            } else {
                block();
            }

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

                // Communicate his reservation price and execution cost
                ACLMessage bidderInformation = new ACLMessage(ACLMessage.INFORM);
                bidderInformation.setConversationId("BidderInformation");
                bidderInformation.addReceiver(evaluationAgent);
                bidderInformation.setContent(myAgent.getName() + "||" + reservationPrice + "||" + executionCost);
                myAgent.send(bidderInformation);
                doDelete();

            } else {
                block();
            }

        }

        @Override
        public boolean done() {
            return false;
        }
    }   
}