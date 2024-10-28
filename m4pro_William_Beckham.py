# This Python script creates a user-friendly Book Inventory System that allows users to display,
# search, and calculate the value of books organized by author, title, and price range, using 
# formatted tables for clear output.
# 10-22-2024
# CSC121 M4pro
# William Beckham

from m4pro_functions import *

def main():
    """
    Main function to run the Book Inventory System.

    It initializes the book inventory and provides a menu for users to interact
    with the inventory system. Users can display inventory, lookup books by
    author, book name, or price range, and exit the program.

    Returns:
        None
    """
    book_inventory = {
        "William Shakespeare": [
            {"book_name": "Hamlet", "year_pub": 1601, "price": 14.52, "quantity": 43},
            {"book_name": "Macbeth", "year_pub": 1606, "price": 13.45, "quantity": 50},
            {"book_name": "Othello", "year_pub": 1604, "price": 15.30, "quantity": 37},
            {"book_name": "Romeo and Juliet", "year_pub": 1597, "price": 12.99, "quantity": 60}
        ],
        "Charles Dickens": [
            {"book_name": "A Tale of Two Cities", "year_pub": 1859, "price": 9.56, "quantity": 75},
            {"book_name": "Great Expectations", "year_pub": 1861, "price": 12.50, "quantity": 60},
            {"book_name": "Oliver Twist", "year_pub": 1837, "price": 9.75, "quantity": 50},
            {"book_name": "David Copperfield", "year_pub": 1850, "price": 11.25, "quantity": 40}
        ],
        "James Joyce": [
            {"book_name": "Ulysses", "year_pub": 1922, "price": 19.99, "quantity": 30},
            {"book_name": "A Portrait of the Artist as a Young Man", "year_pub": 1916, "price": 13.20, "quantity": 25},
            {"book_name": "Dubliners", "year_pub": 1914, "price": 12.00, "quantity": 35},
            {"book_name": "Finnegans Wake", "year_pub": 1939, "price": 16.50, "quantity": 20}
        ],
        "Ernest Hemingway": [
            {"book_name": "The Old Man and the Sea", "year_pub": 1952, "price": 10.35, "quantity": 80},
            {"book_name": "A Farewell to Arms", "year_pub": 1929, "price": 14.75, "quantity": 45},
            {"book_name": "For Whom the Bell Tolls", "year_pub": 1940, "price": 13.50, "quantity": 50},
            {"book_name": "The Sun Also Rises", "year_pub": 1926, "price": 12.99, "quantity": 55}
        ],
        "J.K. Rowling": [
            {"book_name": "Harry Potter and the Philosopher's Stone", "year_pub": 1997, "price": 16.62, "quantity": 100},
            {"book_name": "Harry Potter and the Chamber of Secrets", "year_pub": 1998, "price": 22.99, "quantity": 90},
            {"book_name": "Harry Potter and the Prisoner of Azkaban", "year_pub": 1999, "price": 23.99, "quantity": 85},
            {"book_name": "Harry Potter and the Goblet of Fire", "year_pub": 2000, "price": 25.99, "quantity": 80}
        ]
    }

    continue_program = True

    while continue_program:
        print("\nMenu:")
        print("1. Display Book Inventory and Overall Total")
        print("2. Lookup by Author and Get Total")
        print("3. Lookup by Book Name and Get Total")
        print("4. Lookup by Price Range")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            display_inventory(book_inventory)
        elif choice == '2':
            lookup_by_author(book_inventory)
        elif choice == '3':
            lookup_by_book_name(book_inventory)
        elif choice == '4':
            lookup_by_price_range(book_inventory)
        elif choice == '5':
            confirm = input("Are you sure you want to exit? (y/n): ").strip().lower()
            continue_program = confirm != 'y'  # Set continue_program to False if the user confirms exit
            if not continue_program:
                print("Exiting the program.")
            else:
                print("Returning to menu.")
        else:
            print("Invalid choice. Please select again.")

if __name__ == "__main__":
    main()
