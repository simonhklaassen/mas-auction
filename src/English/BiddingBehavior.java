package English;

import java.text.DecimalFormat;
import java.util.Random;
import java.util.concurrent.ThreadLocalRandom;
import java.util.List;

interface BiddingBehavior {

    static int decimalPlacesRounding = 3;
    static DecimalFormat decimalFormat = new DecimalFormat("0." + "0".repeat(decimalPlacesRounding));

    default double determineHardwareCoefficient(double alpha) {

        double min = 1.0 - alpha;
        double max = 1.0 + alpha;

        double hardwareCoefficient = ThreadLocalRandom.current().nextDouble(min, max);
        hardwareCoefficient = Double.parseDouble(decimalFormat.format(hardwareCoefficient));
        
        return hardwareCoefficient;
    }

    default double determineHardwareCoefficientUnrounded(double alpha) {

        double min = 1.0 - alpha;
        double max = 1.0 + alpha;

        double hardwareCoefficient = ThreadLocalRandom.current().nextDouble(min, max);
        
        return hardwareCoefficient;
    }

    default Double estimateTaskCostliness (Double trueTaskCostliness, Double beta) {

        Double mean = trueTaskCostliness;
        Double sd = beta;

        Random random = new Random();
        Double estimationTaskCostliness = Double.parseDouble(decimalFormat.format(generateNormal(random, mean, sd)));

        return estimationTaskCostliness;
    }

    default double generateStandardNormal(Random random) {

        double u1 = random.nextDouble();
        double u2 = random.nextDouble();

        return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    }

    default double generateNormal(Random random, double mean, double stdDev) {

        return mean + stdDev * generateStandardNormal(random);
    }

    default long calculateCommonCost(int ps, String pc) {

        long commonCost;
        if (pc.equals("logn")) {
            commonCost = (int) Math.ceil(Math.log(ps) / Math.log(2));
        } else if (pc.equals("linear")) {
            commonCost = ps;
        } else if (pc.equals("nlogn")) {
            commonCost = (int) Math.ceil((Math.log(ps) / Math.log(2)) * ps);
        } else {
            commonCost = (int) Math.pow(ps, 2);
        }

        return commonCost;
    }

    default long calculateInitialReservationPrice(long commonCost, double hc, double etc) {

        long initialReservationPrice = (long) Math.ceil(((double) commonCost) * hc * etc);

        return initialReservationPrice;
    }

    default Double calculateDiscrepancyBetweenDistributions(Double avgCD, Double avgID) {
        
        Double ct = (avgCD - avgID) / avgID;
        ct = Double.parseDouble(decimalFormat.format(ct));

        return ct;
    }

    default long adjustReservationPrice (long cc, Double hc, Double etc, Double ac, Double ct) {

        long arp = (int) Math.ceil(cc * hc * (etc + ac * ct));

        return arp;
    }

    default long calculateExecutionCost (long cc, Double hc, Double ttc) {

        long executionCost = (long) Math.ceil((double) cc * hc * ttc);

        return executionCost;
    }

    default Double calculateAvgCorrectionTerm(List<Double> ctpar) {

        int length = ctpar.size();
        double sum = 0;
        for (int i = 0; i < length; i++) {
            sum = sum + ctpar.get(i);
        }
        Double avgCorrectionTerm = sum / length;
        avgCorrectionTerm = Double.parseDouble(decimalFormat.format(avgCorrectionTerm));

        return avgCorrectionTerm;
    }

}
