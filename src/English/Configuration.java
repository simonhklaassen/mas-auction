package English;

public class Configuration {

    // Relevant variables for the cost function
    public static Double alpha = 0.538;
    public static Double beta = 0.05;
    public static Double gamma = 0.5;

    // Relevant parameters for the experimental design
    public static String[] problemComplexities = new String[] {"linear", "nlogn", "quadratic"};
    public static int[] problemSizes = new int[] {100,200,400,800,1600,3200,6400,12800};
    public static int amountOfTasksPerCombination = 3;
    
}