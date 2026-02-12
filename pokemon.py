import os
import time
import requests
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv


# ---------------------------------------
# LOAD ENV VARIABLES
# ---------------------------------------

load_dotenv()
API_KEY = os.getenv("POKEMON_API_KEY")

if not API_KEY:
    raise Exception("POKEMON_API_KEY not set in environment.")

# ---------------------------------------
# CONFIG
# ---------------------------------------

API_BASE_URL = "https://api.pokemontcg.io/v2"
PAGE_SIZE = 250

DB_CONFIG = {
    "host": "localhost",
    "database": "collector",
    "user": "postgres",
    "password": "yourpassword"
}


# ---------------------------------------
# DATABASE CONNECTION
# ---------------------------------------

def get_connection():
    return psycopg2.connect(**DB_CONFIG)


# ---------------------------------------
# INSERT SETS
# ---------------------------------------

def insert_sets(sets_data):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO pokemon_sets (
            id, name, series, release_date,
            printed_total, total
        )
        VALUES (%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO NOTHING
    """

    values = []

    for s in sets_data:
        values.append((
            s["id"],
            s["name"],
            s.get("series"),
            s.get("releaseDate"),
            s.get("printedTotal"),
            s.get("total")
        ))

    execute_batch(cur, sql, values)
    conn.commit()
    cur.close()
    conn.close()

    print(f"Inserted {len(values)} sets.")


# ---------------------------------------
# INSERT CARDS
# ---------------------------------------

def insert_cards(cards_data):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO pokemon_cards (
            id, name, supertype, rarity,
            hp, set_id, number,
            image_small, image_large
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO NOTHING
    """

    values = []

    for card in cards_data:
        hp_value = None
        try:
            if card.get("hp"):
                hp_value = int(card.get("hp"))
        except:
            hp_value = None

        values.append((
            card["id"],
            card["name"],
            card.get("supertype"),
            card.get("rarity"),
            hp_value,
            card.get("set", {}).get("id"),
            card.get("number"),
            card.get("images", {}).get("small"),
            card.get("images", {}).get("large")
        ))

    execute_batch(cur, sql, values)
    conn.commit()
    cur.close()
    conn.close()

    print(f"Inserted {len(values)} cards.")


# ---------------------------------------
# FETCH ALL SETS
# ---------------------------------------

def fetch_sets():
    print("Fetching sets...")

    headers = {"X-Api-Key": API_KEY}

    response = requests.get(
        f"{API_BASE_URL}/sets",
        headers=headers,
        timeout=20
    )
    response.raise_for_status()

    sets_data = response.json()["data"]
    insert_sets(sets_data)


# ---------------------------------------
# FETCH ALL CARDS (Paginated)
# ---------------------------------------

def fetch_all_cards():
    print("Fetching all cards...")

    headers = {"X-Api-Key": API_KEY}
    page = 1
    total_imported = 0

    while True:
        print(f"Fetching page {page}...")

        response = requests.get(
            f"{API_BASE_URL}/cards",
            headers=headers,
            params={
                "page": page,
                "pageSize": PAGE_SIZE
            },
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        cards = data.get("data", [])
        if not cards:
            break

        insert_cards(cards)

        total_imported += len(cards)
        print(f"Total imported so far: {total_imported}")

        page += 1
        time.sleep(0.2)  # Respect API rate limits

    print("All cards imported successfully.")


# ---------------------------------------
# MAIN
# ---------------------------------------

if __name__ == "__main__":
    try:
        fetch_sets()
        fetch_all_cards()
        print("Import completed successfully.")
    except Exception as e:
        print("Error occurred:", e)
