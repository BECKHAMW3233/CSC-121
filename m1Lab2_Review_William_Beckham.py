# Function to evaluate the best investment choice
def evaluate_investments(num_options, initial_investment):
    best_return = float('-inf')
    best_option = None
    best_risk = None

    for i in range(1, num_options + 1):
        print(f"Option {i}")
        up_value = float(input(" Enter high value: "))
        down_value = float(input(" Enter low value: "))

        # Calculate expected end value, expected return, and risk
        expected_end_value = (up_value + down_value) / 2
        expected_return = (expected_end_value - initial_investment) / initial_investment * 100
        risk = (up_value - down_value) / 2

        # Check if this option has the best return so far
        if expected_return > best_return:
            best_return = expected_return
            best_option = i
            best_risk = risk

    # Output the best investment choice
    print(f"Best investment:  {best_option}")
    print(f"Best average return = {best_return:.1f} %")
    print(f"Risk = {best_risk:.1f}")

# Main part of the program
if __name__ == "__main__":
    num_options = int(input("Enter number of investment options: "))
    initial_investment = float(input("Enter start value: "))
    evaluate_investments(num_options, initial_investment)
