# Use of decision structures, loops, functions, and lists within a program
# 9-25-2024
# CSC-121 m3Pro - Purchases
# William Beckham


from m3pro_functions import book_display, show_purchase, calculate_total

# Book Data
authors = [
    "William Shakespeare", 
    "Charles Dickens", 
    "James Joyce", 
    "Ernest Hemingway", 
    "J.K. Rowling"
]
books = [
    "Hamlet", 
    "A Tale of Two Cities", 
    "Ulysses", 
    "The Old Man and the Sea", 
    "Harry Potter and the Philosopher's Stone"
]
published = [1601, 1859, 1922, 1952, 1997]
prices = [14.52, 9.56, 19.97, 10.35, 16.62]

# Sales tax rate
sales_tax_rate = 0.05

# Main Program Flow
def main():
    """
    Main function to run the book purchasing program.
    Displays available books, takes user input for selected books,
    calculates total price including sales tax, and displays the summary.
    """
    book_display(books, authors, published, prices)
    
    # List to store selected book numbers
    book_nums = []
    continue_shopping = True  # Flag to control the shopping loop

    while continue_shopping:
        # Get user input for book selection
        try:
            book_num = int(input("Enter the number of the book you'd like to purchase: "))
            if 1 <= book_num <= len(books):
                book_nums.append(book_num)  # Add valid book number to the list
            else:
                print(f"Invalid number. Please enter a number between 1 and {len(books)}.")
        except ValueError:
            print("Please enter a valid number.")
        
        # Ask if the user wants to purchase another book
        another = input("Do you want to purchase another book? (yes/y or no/n): ").strip().lower()
        if another in ['no', 'n']:
            continue_shopping = False  # Set the flag to False to exit the loop

    # Show the books selected for purchase
    if book_nums:
        show_purchase(book_nums, books, authors, published, prices)
        
        # Calculate total price and total with tax
        total_price, total_with_sales_tax = calculate_total(book_nums, prices, sales_tax_rate)
        
        # Display total price and total with sales tax
        print("Total Price (cost of book(s) + 5% tax:)")
        print(f"Total Price (before tax): ${total_price:.2f}")
        print(f"Sales Tax (5%): ${total_with_sales_tax - total_price:.2f}")
        print(f"Total Price (with tax): ${total_with_sales_tax:.2f}")
    else:
        print("No books were selected for purchase.")

# Run the program
if __name__ == "__main__":
    main()
