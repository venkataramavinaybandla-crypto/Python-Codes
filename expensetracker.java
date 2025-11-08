import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.print("Enter your Annual Salary (in Rs): ");
        double salary = sc.nextDouble();

        double taxRate = getTaxRate(salary);
        double tax = (salary * taxRate) / 100;
        double salaryAfterTax = salary - tax;

        double fixedExpenses = (salaryAfterTax * 10) / 100; // assume 10% of post-tax salary
        double finalAnnualBalance = salaryAfterTax - fixedExpenses;
        double finalMonthlyBalance = finalAnnualBalance / 12;

        System.out.println("\n--- Salary Breakdown ---");
        System.out.println("Annual Salary: Rs." + salary);
        System.out.println("Tax Deducted (" + taxRate + "%): Rs." + tax);
        System.out.println("Other Fixed Expenses (10%): Rs." + fixedExpenses);
        System.out.println("Available Annual Balance: Rs." + finalAnnualBalance);
        System.out.println("Available Monthly Balance: Rs." + finalMonthlyBalance);

        ArrayList<String> names = new ArrayList<>();
        ArrayList<String> cat = new ArrayList<>();
        ArrayList<Double> amt = new ArrayList<>();
        ArrayList<String> date = new ArrayList<>();

        double minBalance = 0;
        double totalSavings = 0;

        int choice;
        do {
            System.out.println("\n--- Main Menu ---");
            System.out.println("1. Add Expense");
            System.out.println("2. View Expenses");
            System.out.println("3. Total Expense");
            System.out.println("4. Savings");
            System.out.println("5. Eligible Loan Range");
            System.out.println("6. Exit");
            System.out.print("Enter your choice: ");
            choice = sc.nextInt();
            sc.nextLine();

            switch (choice) {
                case 1:
                    System.out.print("Enter Expense Name: ");
                    String n = sc.nextLine();
                    System.out.print("Enter Category: ");
                    String c = sc.nextLine();
                    System.out.print("Enter Amount: ");
                    double a = sc.nextDouble();
                    sc.nextLine();
                    System.out.print("Enter Date (dd/mm/yyyy): ");
                    String d = sc.nextLine();

                    names.add(n);
                    cat.add(c);
                    amt.add(a);
                    date.add(d);

                    System.out.println("Expense Added Successfully!");
                    break;

                case 2:
                    System.out.println("\n--- Expense Report ---");
                    System.out.println("Tax Deducted: Rs." + tax);
                    System.out.println("Other Fixed Expenses: Rs." + fixedExpenses);
                    System.out.println("Available Monthly Balance: Rs." + finalMonthlyBalance);
                    System.out.println("Available Annual Balance: Rs." + finalAnnualBalance);

                    if (names.isEmpty()) {
                        System.out.println("No additional expenses recorded.");
                    } else {
                        for (int i = 0; i < names.size(); i++) {
                            System.out.println((i + 1) + ". " + names.get(i) + " | " +
                                    cat.get(i) + " | Rs." + amt.get(i) + " | " + date.get(i));
                        }
                    }
                    break;

                case 3:
                    double totalExpense = 0;
                    for (double x : amt) totalExpense += x;

                    double balanceAfterExpenses = finalMonthlyBalance - totalExpense;
                    System.out.println("Total Extra Expense: Rs." + totalExpense);
                    System.out.println("Balance Remaining This Month: Rs." + balanceAfterExpenses);
                    break;

                case 4:
                    if (minBalance == 0) {
                        System.out.print("Enter your minimum balance goal: ");
                        minBalance = sc.nextDouble();
                    }

                    double totalMonthlyExpense = 0;
                    for (double x : amt) totalMonthlyExpense += x;
                    totalSavings = finalMonthlyBalance - totalMonthlyExpense;

                    System.out.println("\n--- Savings Overview ---");
                    System.out.println("Minimum Balance Goal: Rs." + minBalance);
                    System.out.println("Current Savings: Rs." + totalSavings);

                    if (totalSavings <= minBalance + 1000) {
                        System.out.println("Alert: You are near your minimum balance limit!");
                    } else if (totalSavings < minBalance) {
                        System.out.println("Warning: You have fallen below your minimum balance!");
                    } else {
                        System.out.println("Status: Savings are in a safe range.");
                    }
                    break;

                case 5:
                    double[] loanRange = getLoanRange(finalMonthlyBalance);
                    System.out.println("\n--- Eligible Home Loan Range ---");
                    System.out.println("Based on your monthly income:");
                    System.out.println("Minimum Loan: Rs." + loanRange[0]);
                    System.out.println("Maximum Loan: Rs." + loanRange[1]);
                    break;

                case 6:
                    System.out.println("Exiting... Goodbye!");
                    break;

                default:
                    System.out.println("Invalid choice!");
            }
        } while (choice != 6);

        sc.close();
    }

    public static double getTaxRate(double salary) {
        if (salary <= 400000) return 0;
        else if (salary <= 800000) return 5;
        else if (salary <= 1200000) return 10;
        else if (salary <= 1600000) return 15;
        else if (salary <= 2000000) return 20;
        else if (salary <= 2400000) return 25;
        else return 30;
    }

    public static double[] getLoanRange(double monthlyIncome) {
        double[] range = new double[2];
        if (monthlyIncome <= 25000) {
            range[0] = 700000; range[1] = 1400000;
        } else if (monthlyIncome <= 50000) {
            range[0] = 1700000; range[1] = 3300000;
        } else if (monthlyIncome <= 70000) {
            range[0] = 3000000; range[1] = 5800000;
        } else {
            range[0] = 4000000; range[1] = 7500000;
        }
        return range;
    }
}
