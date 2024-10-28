# Python script to evaluate multiple investment choices and determine the best one based on expected return.
# 08-26-2024
# CSC121 m1Lab2– Review
# William Beckham

def get_investment_details(option_number):
    """Get optimistic and pessimistic values for a given investment option."""
    # - Print the current investment option number.
    # - Prompt the user to enter the optimistic (high) value for this option.
    # - Prompt the user to enter the pessimistic (low) value for this option.
    # - Return both the optimistic and pessimistic values.

    print(f"Option {option_number}")
    up_value = float(input(" Enter high value: "))
    down_value = float(input(" Enter low value: "))
    return up_value, down_value

def calculate_expected_return_and_risk(up_value, down_value, initial_investment):
    """Calculate the expected return and risk for an investment."""
    # - Calculate the expected end value as the average of the optimistic and pessimistic values.
    # - Calculate the expected return as the percentage difference between the expected end value and the initial investment.
    # - Calculate the risk as half of the difference between the optimistic and pessimistic values.
    # - Return both the expected return and risk.

    expected_end_value = (up_value + down_value) / 2
    expected_return = (expected_end_value - initial_investment) / initial_investment * 100  # in percentage
    risk = (up_value - down_value) / 2
    return expected_return, risk

def evaluate_investments(num_choices, initial_investment):
    """Evaluate all investment options and determine the best one."""
    # - Initialize variables to keep track of the best return, the best option number, and the associated risk.
    # - Loop over each investment option (from 1 to the number of choices):
    #   - Get the optimistic and pessimistic values for the current option.
    #   - Calculate the expected return and risk for the current option.
    #   - Print the expected return and risk for the current option.
    #   - If the expected return for the current option is better than the best return so far:
    #     - Update the best return, the best option number, and the best risk.
    # - After the loop, return the best option number, the best return, and the associated risk.

    best_return = 0  # Running total for the best average return
    best_option = 0  # Running total for the best investment option number
    best_risk = 0  # Variable to save the calculated risk of the best investment option

    for option in range(1, num_choices + 1):
        up_value, down_value = get_investment_details(option)
        expected_return, risk = calculate_expected_return_and_risk(up_value, down_value, initial_investment)

        # Print the results
        print(f"Expected Return = {expected_return:.2f} %")
        print(f"Risk = {risk:.2f}")

        # Check if the current expected return is the best so far
        if expected_return > best_return:
            best_return = expected_return
            best_option = option
            best_risk = risk

    return best_option, best_return, best_risk

def main():
    """Main function to run the investment evaluator."""
    # - Initialize num_choices with a value that allows the loop to start.
    # - Enter a loop that continues until the user enters 0 for the number of choices:
    #   - Prompt the user to enter the number of investment options (or 0 to exit).
    #   - If the user enters 0, print an exit message and end the program.
    #   - Otherwise, prompt the user to enter the initial investment amount.
    #   - Evaluate the investment options and determine the best one.
    #   - Print the best investment option, the best average return, and the associated risk.
    # - The loop will repeat until the user chooses to exit.

    num_choices = -1  # Initialize with a value that allows entering the loop

    while num_choices != 0:
        num_choices = int(input("Enter number of investment options (or 0 to exit): "))
        
        if num_choices == 0:
            print("Exiting the program.")
            return

        initial_investment = float(input("Enter start value: "))

        best_option, best_return, best_risk = evaluate_investments(num_choices, initial_investment)

        # Display the best investment option information
        print(f"\nBest investment:  {best_option}")
        print(f"Best average return = {best_return:.1f} %")
        print(f"Risk = {best_risk:.1f}")
        print("\n---\n")

# Run the main function
if __name__ == "__main__":
    main()
