import java.util.*;
import java.io.*;

class Expense {
    private String name;
    private String category;
    private double amount;
    private String date;

    public Expense(String name, String category, double amount, String date) {
        this.name = name;
        this.category = category;
        this.amount = amount;
        this.date = date;
    }

    public double getAmount() {
        return amount;
    }

    public String toFileString() {
        return name + "|" + category + "|" + amount + "|" + date;
    }

    public static Expense fromFileString(String line) {
        String[] parts = line.split("\\|");
        if (parts.length != 4) return null;
        String name = parts[0];
        String category = parts[1];
        double amount = Double.parseDouble(parts[2]);
        String date = parts[3];
        return new Expense(name, category, amount, date);
    }

    @Override
    public String toString() {
        return name + " | " + category + " | Rs." + amount + " | " + date;
    }
}

class FinancialManager {
    private double salary;
    private double taxRate;
    private double tax;
    private double fixedExpenses;
    private double finalAnnualBalance;
    private double finalMonthlyBalance;
    private ArrayList<Expense> expenses;
    private double minBalanceGoal;

    public FinancialManager(double salary) {
        this.salary = salary;
        this.taxRate = calculateTaxRate(salary);
        this.tax = (salary * taxRate) / 100;
        double salaryAfterTax = salary - tax;
        this.fixedExpenses = salaryAfterTax * 0.10;
        this.finalAnnualBalance = salaryAfterTax - fixedExpenses;
        this.finalMonthlyBalance = finalAnnualBalance / 12;
        this.expenses = new ArrayList<>();
        this.minBalanceGoal = 0;
    }

    private double calculateTaxRate(double salary) {
        if (salary <= 400000) return 0;
        else if (salary <= 800000) return 5;
        else if (salary <= 1200000) return 10;
        else if (salary <= 1600000) return 15;
        else if (salary <= 2000000) return 20;
        else if (salary <= 2400000) return 25;
        else return 30;
    }

    public void addExpense(Expense expense) {
        expenses.add(expense);
    }

    public void setMinBalanceGoal(double minBalance) {
        this.minBalanceGoal = minBalance;
    }

    public double getMinBalanceGoal() {
        return minBalanceGoal;
    }

    public double getTotalExpenses() {
        double total = 0;
        for (Expense e : expenses) {
            total += e.getAmount();
        }
        return total;
    }

    public double getSavings() {
        return finalMonthlyBalance - getTotalExpenses();
    }

    public void printSalaryDetails() {
        System.out.println("\n--- Salary Breakdown ---");
        System.out.println("Annual Salary: Rs." + salary);
        System.out.println("Tax Deducted (" + taxRate + "%): Rs." + tax);
        System.out.println("Other Fixed Expenses (10%): Rs." + fixedExpenses);
        System.out.println("Available Annual Balance: Rs." + finalAnnualBalance);
        System.out.println("Available Monthly Balance: Rs." + finalMonthlyBalance);
    }

    public void printExpenses() {
        System.out.println("\n--- Expense Report ---");
        if (expenses.isEmpty()) {
            System.out.println("No additional expenses recorded.");
        } else {
            int count = 1;
            for (Expense e : expenses) {
                System.out.println(count++ + ". " + e);
            }
        }
    }

    public void printSavingsStatus() {
        double savings = getSavings();
        System.out.println("\n--- Savings Overview ---");
        System.out.println("Minimum Balance Goal: Rs." + minBalanceGoal);
        System.out.println("Current Savings: Rs." + savings);

        if (savings <= minBalanceGoal + 1000) {
            System.out.println("Alert: You are near your minimum balance limit!");
        } else if (savings < minBalanceGoal) {
            System.out.println("Warning: You have fallen below your minimum balance!");
        } else {
            System.out.println("Status: Savings are in a safe range.");
        }
    }

    public double[] getLoanRange() {
        double[] range = new double[2];
        if (finalMonthlyBalance <= 25000) {
            range[0] = 700000; range[1] = 1400000;
        } else if (finalMonthlyBalance <= 50000) {
            range[0] = 1700000; range[1] = 3300000;
        } else if (finalMonthlyBalance <= 70000) {
            range[0] = 3000000; range[1] = 5800000;
        } else {
            range[0] = 4000000; range[1] = 7500000;
        }
        return range;
    }

    public void saveExpensesToFile(String filename) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filename))) {
            for (Expense e : expenses) {
                writer.write(e.toFileString());
                writer.newLine();
            }
        }
    }

    public void loadExpensesFromFile(String filename) throws IOException {
        expenses.clear();
        try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            String line;
            while ((line = reader.readLine()) != null) {
                Expense e = Expense.fromFileString(line);
                if (e != null) expenses.add(e);
            }
        }
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        double salary = 0;

        while (true) {
            try {
                System.out.print("Enter your Annual Salary (in Rs): ");
                salary = sc.nextDouble();
                if (salary < 0) throw new InputMismatchException();
                break;
            } catch (InputMismatchException e) {
                System.out.println("Invalid input! Please enter a valid positive number.");
                sc.nextLine(); // Clear invalid input
            }
        }

        FinancialManager manager = new FinancialManager(salary);
        int choice;

        do {
            System.out.println("\n--- Main Menu ---");
            System.out.println("1. Add Expense");
            System.out.println("2. View Expenses");
            System.out.println("3. Total Expense and Balance");
            System.out.println("4. Savings Overview");
            System.out.println("5. Eligible Loan Range");
            System.out.println("6. Save Expenses");
            System.out.println("7. Load Expenses");
            System.out.println("8. Set Minimum Balance Goal");
            System.out.println("9. Exit");
            System.out.print("Enter your choice: ");
            
            choice = -1;
            try {
                choice = sc.nextInt();
                sc.nextLine(); // Consume newline
            } catch (InputMismatchException e) {
                System.out.println("Please enter a valid number.");
                sc.nextLine();
                continue;
            }

            switch (choice) {
                case 1:
                    System.out.print("Enter Expense Name: ");
                    String name = sc.nextLine();
                    System.out.print("Enter Category: ");
                    String category = sc.nextLine();

                    double amount = 0;
                    while (true) {
                        try {
                            System.out.print("Enter Amount: ");
                            amount = sc.nextDouble();
                            if (amount < 0) throw new InputMismatchException();
                            sc.nextLine();
                            break;
                        } catch (InputMismatchException e) {
                            System.out.println("Invalid amount! Please enter a positive number.");
                            sc.nextLine();
                        }
                    }

                    System.out.print("Enter Date (dd/mm/yyyy): ");
                    String date = sc.nextLine();

                    manager.addExpense(new Expense(name, category, amount, date));
                    System.out.println("Expense Added Successfully!");
                    break;

                case 2:
                    manager.printExpenses();
                    break;

                case 3:
                    manager.printSalaryDetails();
                    System.out.println("Total Extra Expense: Rs." + manager.getTotalExpenses());
                    System.out.println("Balance Remaining This Month: Rs." + manager.getSavings());
                    break;

                case 4:
                    if (manager.getMinBalanceGoal() == 0) {
                        System.out.print("Enter your minimum balance goal: ");
                        try {
                            double minGoal = sc.nextDouble();
                            if (minGoal < 0) {
                                System.out.println("Goal cannot be negative.");
                            } else {
                                manager.setMinBalanceGoal(minGoal);
                            }
                        } catch (InputMismatchException e) {
                            System.out.println("Invalid input, minimum balance goal not set.");
                            sc.nextLine();
                        }
                    }
                    manager.printSavingsStatus();
                    break;

                case 5:
                    double[] loanRange = manager.getLoanRange();
                    System.out.println("\n--- Eligible Home Loan Range ---");
                    System.out.println("Based on your monthly income:");
                    System.out.println("Minimum Loan: Rs." + loanRange[0]);
                    System.out.println("Maximum Loan: Rs." + loanRange[1]);
                    break;

                case 6:
                    try {
                        manager.saveExpensesToFile("expenses.txt");
                        System.out.println("Expenses saved successfully.");
                    } catch (IOException e) {
                        System.out.println("Error saving expenses: " + e.getMessage());
                    }
                    break;

                case 7:
                    try {
                        manager.loadExpensesFromFile("expenses.txt");
                        System.out.println("Expenses loaded successfully.");
                    } catch (IOException e) {
                        System.out.println("Error loading expenses: " + e.getMessage());
                    }
                    break;

                case 8:
                    System.out.print("Enter your minimum balance goal: ");
                    try {
                        double minGoal = sc.nextDouble();
                        if (minGoal < 0) {
                            System.out.println("Goal cannot be negative.");
                        } else {
                            manager.setMinBalanceGoal(minGoal);
                        }
                        sc.nextLine();
                    } catch (InputMismatchException e) {
                        System.out.println("Invalid input.");
                        sc.nextLine();
                    }
                    break;

                case 9:
                    System.out.println("Exiting... Goodbye!");
                    break;

                default:
                    System.out.println("Invalid choice! Please select from the menu.");
            }
        } while (choice != 9);

        sc.close();
    }
}
