# 10-22-2024
# CSC121 M4pro_functions
# William Beckham

def display_inventory(book_inventory):
    """
    Displays the entire book inventory along with the total inventory value.

    Args:
        book_inventory (dict): A dictionary containing authors and their books.

    Returns:
        None
    """
    print("\nInventory:")
    print(f"{'Author':<25} {'Book Name':<50} {'Year':<8} {'Price':<8} {'Quantity':<10}")
    print("-" * 105)
    
    total_value = sum(book['price'] * book['quantity'] for books in book_inventory.values() for book in books)
    
    for author, books in book_inventory.items():
        for book in books:
            print(f"{author:<25} {book['book_name']:<50} {book['year_pub']:<8} ${book['price']:<8.2f} {book['quantity']:<10}")
    
    print("-" * 105)
    # Aligning the overall total to the right, so it matches the price column
    print(f"{'Overall Total:':<85} ${total_value:>8.2f}")  # Adjusted for right alignment

def lookup_by_author(book_inventory):
    """
    Looks up books by a specific author and displays their total value.

    Args:
        book_inventory (dict): A dictionary containing authors and their books.

    Returns:
        None
    """
    author = input("Enter the author's name (case-sensitive): ")

    if author not in book_inventory:
        print(f"Author '{author}' not found in the inventory.")
        return  # Early exit if author not found

    print(f"\nBooks by {author}:")
    print("-" * 70)
    print(f"{'Book Name':<50} {'Year':<10} {'Price':<10} {'Quantity':<10}")
    print("-" * 70)

    total_value = sum(book['price'] * book['quantity'] for book in book_inventory[author])
    
    for book in book_inventory[author]:
        print(f"{book['book_name']:<50} {book['year_pub']:<10} ${book['price']:<9.2f} {book['quantity']:<10}")

    print("-" * 70)
    print(f"\nTotal value of books by {author}: ${total_value:.2f}")


def lookup_by_book_name(book_inventory):
    """
    Looks up a book by its name and displays its details and total price.

    Args:
        book_inventory (dict): A dictionary containing authors and their books.

    Returns:
        None
    """
    book_name = input("Enter the name of the book (case-sensitive): ")

    found = False
    for author, books in book_inventory.items():
        for book in books:
            if book['book_name'] == book_name:
                found = True
                total_price = book['price'] * book['quantity']
                print("\nBook found:")
                print("-" * 70)
                print(f"{'Author':<25} {'Book Name':<50} {'Year':<10} {'Price':<10} {'Quantity':<10}")
                print("-" * 70)
                print(f"{author:<25} {book['book_name']:<50} {book['year_pub']:<10} ${book['price']:<9.2f} {book['quantity']:<10}")
                print("-" * 70)
                print(f"\nTotal price for {book['book_name']}: ${total_price:.2f}")

    if not found:
        print(f"Book '{book_name}' not found in the inventory.")


def lookup_by_price_range(book_inventory):
    """
    Looks up books within a specific price range and displays them.

    Args:
        book_inventory (dict): A dictionary containing authors and their books.

    Returns:
        None
    """
    start_price = float(input("Enter the starting price: "))
    end_price = float(input("Enter the ending price: "))
    
    found_books = [
        (author, book) for author, books in book_inventory.items()
        for book in books if start_price <= book['price'] <= end_price
    ]

    if not found_books:
        print(f"No books found between ${start_price:.2f} and ${end_price:.2f}.")
        return  # Early exit if no books found

    print(f"\nBooks priced between ${start_price:.2f} and ${end_price:.2f}:")
    print("-" * 85)
    print(f"{'Author':<25} {'Book Name':<50} {'Year':<10} {'Price':<10} {'Quantity':<10}")
    print("-" * 85)

    for author, book in found_books:
        print(f"{author:<25} {book['book_name']:<50} {book['year_pub']:<10} ${book['price']:<9.2f} {book['quantity']:<10}")

    print("-" * 85)
    print(f"\nTotal number of books in this range: {len(found_books)}")
