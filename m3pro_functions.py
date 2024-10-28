# Use of decision structures, loops, functions, and lists within a program
# 9-25-2024
# CSC-121 m3Pro - Purchases
# William Beckham

def book_display(books, authors, published, prices):
    """
    Display a formatted list of books along with their authors, publication years, and prices.

    This function takes four lists: books, authors, published years, and prices,
    and prints them in a tabular format for the user to view.

    Parameters:
    - books (list of str): List of book titles.
    - authors (list of str): List of authors corresponding to the books.
    - published (list of int): List of publication years corresponding to the books.
    - prices (list of float): List of prices corresponding to the books.

    Returns:
    None: This function does not return a value. It prints the book information directly.
    """
    print(f"{'Num':<5}{'Book':<48} {'Author':<25} {'Published':<18} {'Price':<15}")
    print("-" * 120)
    for i, (book, author, pub, price) in enumerate(zip(books, authors, published, prices), start=1):
        print(f"{i:<4} {book:<46} {author:<30} {pub:<15} ${price:<15.2f}")
    print("-" * 120)


def show_purchase(book_nums, books, authors, published, prices):
    """
    Display the details of the selected books for purchase.

    This function takes a list of selected book numbers and retrieves the corresponding
    details from the provided lists of books, authors, publication years, and prices. 
    It formats and prints this information for the user to review their selections.

    Parameters:
    - book_nums (list of int): List of indices representing the selected books.
    - books (list of str): List of book titles.
    - authors (list of str): List of authors corresponding to the books.
    - published (list of int): List of publication years corresponding to the books.
    - prices (list of float): List of prices corresponding to the books.

    Returns:
    None: This function does not return a value. It prints the selected book information directly.
    """
    print("\nYou selected the following books for purchase:")
    print(f"{'Book':<48} {'Author':<25} {'Published':<12} {'Price':>10}")
    print("-" * 120)
    for num in book_nums:
        book_index = num - 1  # Adjust for zero-indexing
        print(f"{books[book_index]:<48} {authors[book_index]:<25} {published[book_index]:<17} ${prices[book_index]:<9.2f}")
    print("-" * 120)


def calculate_total(book_nums, prices, sales_tax_rate):
    """
    Calculate the total price of selected books including sales tax.

    This function computes the total price of the books selected by the user
    and applies a sales tax to determine the final amount due. The function 
    adjusts for zero-based indexing when accessing prices.

    Parameters:
    - book_nums (list of int): List of indices representing the selected books.
    - prices (list of float): List of prices corresponding to the books.
    - sales_tax_rate (float): The sales tax rate to be applied (as a decimal).

    Returns:
    - total_price (float): The total price of the selected books before tax.
    - total_with_tax (float): The total price of the selected books after applying sales tax.
    """
    total_price = sum(prices[num - 1] for num in book_nums)  # Adjust for zero-indexing
    total_with_tax = total_price * (1 + sales_tax_rate)
    return total_price, total_with_tax
