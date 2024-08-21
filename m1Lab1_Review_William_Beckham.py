# This Python code calculates a user's Body Mass Index (BMI) based on their
# weight and height. It evaluates the BMI to determine if it's within the
# healthy range, and if not, it provides guidance on how much weight to lose
# or gain to reach a healthy BMI
# 08/21/2024
# CSC121 m1Lab1– Review
# William Beckham


print("Enter 'end' to quit at anytime.")
print()

def calculate_bmi(weight, height):
    # BMI formula: weight (lb) / [height (in)]^2 * 703
    bmi = (weight / (height ** 2)) * 703
    return bmi

def bmi_evaluation(bmi, height, weight):
    if 18.5 <= bmi <= 24.9:
        print()
        return "Your BMI is in the healthy range."
    elif bmi > 24.9:
        print()
        healthy_weight_upper = 24.9 * (height ** 2) / 703
        weight_to_lose = weight - healthy_weight_upper
        return f"Weight to lose to reach a healthy BMI: {weight_to_lose:.2f} lbs"
    elif bmi < 18.5:
        print()
        healthy_weight_lower = 18.5 * (height ** 2) / 703
        weight_to_gain = healthy_weight_lower - weight
        return f"Weight to gain to reach a healthy BMI: {weight_to_gain:.2f} lbs"

def get_input(prompt):
    user_input = input(prompt).strip().lower()
    if user_input == 'end':
        print("Exiting the program. Goodbye!")
        exit()
    return user_input

def get_valid_height():
    while True:
        height = get_input("Enter your height in inches: ")
        try:
            height = float(height)
            if height > 120:  # Example threshold for a height that's too large (10 feet)
                print("The height entered seems too large. Please enter a valid height.")
            else:
                return height
        except ValueError:
            print("Invalid input. Please enter a numeric value for height.")

def main():
    while True:
        # Prompt the user for their height
        height = get_valid_height()

        # Prompt the user for their weight
        weight = get_input("Enter your weight in pounds: ")
        try:
            weight = float(weight)
        except ValueError:
            print("Invalid input. Please enter a numeric value for weight.")
            continue

        # Calculate BMI
        bmi = calculate_bmi(weight, height)
        
        # Display the BMI
        print(f"Your BMI is: {bmi:.2f}")
        
        # Evaluate and display BMI category and weight recommendations
        evaluation = bmi_evaluation(bmi, height, weight)
        print(evaluation)
        print()
        # Ask the user if they want to enter new data
        repeat = get_input("Would you like to run this program again? (Enter 'no' to exit): ")
        print()
        
        if repeat in ('no', 'n'):
            print()
            print("Thank you, Goodbye!")
            break

if __name__ == "__main__":
    main()
