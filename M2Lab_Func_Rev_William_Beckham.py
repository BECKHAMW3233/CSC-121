# Importing functions from another program to work in this program
# 09-10-2024
# CSC121 m2Lab– Function Review
# William Beckham

# Importing functions from the parking_fee_calculator module
from parking_fee_calculator import getParkingHours, calcParkingFee

# Function to display the menu options to the user
def display_menu():
    # Display menu with two options: calculate parking fee or exit
    print("\nMenu---------------")
    print("1) Calculate parking fee")
    print("2) Exit")
    print("---------------------")


# Main function to handle user choices
def main():
    # Start an infinite loop to continuously show the menu until the user exits
    while True:
        display_menu()  # Show the menu options
        try:
            # Prompt the user to enter their choice (1 or 2)
            choice = int(input("Enter your choice (1 or 2): "))

            # If the user selects option 1, calculate the parking fee
            if choice == 1:
                hours = getParkingHours()  # Get the number of hours parked
                fee = calcParkingFee(hours)  # Calculate the parking fee
                # Display the calculated fee to the user
                print(f"The total parking fee is: ${fee:.2f}")

            # If the user selects option 2, exit the program
            elif choice == 2:
                print("Exiting program. Goodbye!")
                return  # Exit the main function and thus the program
            
            # If the user enters an invalid choice, show an error message
            else:
                print(f"Invalid choice '{choice}'. Please enter 1 or 2.")

        # Handle invalid input (non-numeric values) and prompt the user again
        except ValueError:
            print("Invalid input. Please enter a valid number.")

# Call the main function if the script is executed directly
if __name__ == "__main__":
    main()
