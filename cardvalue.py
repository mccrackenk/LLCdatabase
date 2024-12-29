import requests
import sqlite3
import pandas as pd
from bs4 import BeautifulSoup

# Connect to your SQLite database
conn = sqlite3.connect('pokemon_cards.db')
cursor = conn.cursor()

# Function to fetch card prices (example using PriceCharting for illustration)
def fetch_card_price(card_name, card_set):
    try:
        # Format the query for the URL
        query = f"{card_name} {card_set}".replace(" ", "+")
        url = f"https://www.pricecharting.com/search?q={query}"
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the first listed price (example CSS selectors, adjust based on the website)
        price_elem = soup.select_one('.price .amount')
        if price_elem:
            return float(price_elem.text.strip().replace('$', '').replace(',', ''))
        else:
            return None  # No price found
    except Exception as e:
        print(f"Error fetching price for {card_name} ({card_set}): {e}")
        return None

# Update prices in the database
def update_card_prices():
    # Retrieve all cards from the database
    cursor.execute("SELECT CardID, CardName, CardSet FROM PokemonCards")
    cards = cursor.fetchall()

    for card_id, card_name, card_set in cards:
        print(f"Fetching price for: {card_name} ({card_set})")
        price = fetch_card_price(card_name, card_set)
        
        if price is not None:
            # Update the card with the fetched price
            cursor.execute(
                "ALTER TABLE PokemonCards ADD COLUMN IF NOT EXISTS Price REAL"
            )
            cursor.execute(
                "UPDATE PokemonCards SET Price = ? WHERE CardID = ?",
                (price, card_id)
            )
            print(f"Updated {card_name} ({card_set}) with price: ${price}")
        else:
            print(f"Price not found for {card_name} ({card_set})")

    # Commit changes to the database
    conn.commit()

# Run the price updater
if __name__ == "__main__":
    update_card_prices()

# Close the database connection
conn.close()
