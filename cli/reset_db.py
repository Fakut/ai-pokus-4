# cli/reset_db.py
"""
Reset databáze pro nový start
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.cold_calling_db import ColdCallingDB
import sqlite3


def main():
    print("=" * 60)
    print("   🔄 RESET DATABÁZE")
    print("=" * 60)
    
    choice = input("""
Vyber možnost:
  1. Reset statusů kontaktů (kampaně zůstanou)
  2. Smazat všechny hovory
  3. SMAZAT VŠE (kampaně, kontakty, hovory)
  
Volba (1-3): """).strip()
    
    db = ColdCallingDB()
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    if choice == "1":
        # Reset statusů
        print("\n🔄 Resetuji statusy kontaktů na 'pending'...")
        cursor.execute("UPDATE contacts SET status = 'pending'")
        count = cursor.rowcount
        conn.commit()
        print(f"✅ Resetováno: {count} kontaktů")
        
    elif choice == "2":
        # Smaž hovory
        print("\n🗑️  Mažu všechny hovory...")
        cursor.execute("DELETE FROM calls")
        count = cursor.rowcount
        cursor.execute("UPDATE contacts SET status = 'pending'")
        conn.commit()
        print(f"✅ Smazáno: {count} hovorů")
        print(f"✅ Statusy resetovány")
        
    elif choice == "3":
        # Smaž VŠE
        if input("\n⚠️  OPRAVDU smazat VŠE? (ano/ne): ").lower() == "ano":
            print("\n🗑️  Mažu VŠECHNO...")
            cursor.execute("DELETE FROM calls")
            cursor.execute("DELETE FROM contacts")
            cursor.execute("DELETE FROM campaigns")
            conn.commit()
            print(f"✅ Databáze vymazána!")
        else:
            print("Zrušeno.")
    else:
        print("❌ Neplatná volba!")
    
    conn.close()
    print("\n✅ HOTOVO!")


if __name__ == "__main__":
    main()