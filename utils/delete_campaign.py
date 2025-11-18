import sqlite3

def delete_campaign(campaign_id: int, db_path="data/calls.db"):
    """Smaže kampaň včetně všech kontaktů, které k ní patří.
       Po smazání lze stejné ID použít pro novou kampaň."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Smaž všechny kontakty dané kampaně
    cursor.execute("DELETE FROM contacts WHERE campaign_id=?", (campaign_id,))
    # Smaž samotnou kampaň
    cursor.execute("DELETE FROM campaigns WHERE id=?", (campaign_id,))
    conn.commit()

    # Resetuje sekvenci (autoincrement) pro campaigns, pokud chceš úplně začít od nuly
    # cursor.execute("DELETE FROM sqlite_sequence WHERE name='campaigns'")
    # conn.commit()

    conn.close()
    print(f"Kampaň {campaign_id} a její kontakty byly kompletně smazány.")