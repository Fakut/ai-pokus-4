# 🔐 Kampaně - Izolace Per Účet

## Co se změnilo?

Teď **každý uživatel vidí jen své vlastní kampaně**.

### Změny v databázi:

**`campaigns` tabulka:**
```sql
id              - ID kampaně
name            - Název
description     - Popis
user_id         - ✨ NOVÉ - ID vlastníka kampaně
created_at      - Kdy vytvořena
status          - Status
```

### Jak funguje?

1. **Když vytvoříš kampaň:**
   ```python
   campaign_id = cold_db.create_campaign(
       name="Moje kampaň",
       description="...",
       user_id=session['user_id']  # ✨ Tvůj účet
   )
   ```
   → Kampaň se uloží s tvým `user_id`

2. **Když se přihlásíš:**
   ```python
   campaigns = cold_db.get_campaigns(user_id=session['user_id'])
   # Vrátí jen tvoje kampaně + starší bez user_id
   ```
   → Vidíš jen **své** kampaně

3. **Bezpečnost v detailu:**
   ```python
   # V admin_campaign() route:
   SELECT * FROM campaigns 
   WHERE id = ? 
   AND (user_id = ? OR user_id IS NULL)
   ```
   → Lze přistoupit jen své kampani

---

## Prakticky:

### ✅ Uživatel A
- Vytvoří kampaň "Prodej webů"
- Uloží se jako: `user_id=1`
- Vidí jen **svou** kampaň

### ✅ Uživatel B
- Vidí jen **své** kampaně
- **Nevidí** Uživatele A kampaň
- Pokud se pokusí přistoupit: **ACCESS DENIED**

### ✅ Starší kampaně (bez user_id)
- Všichni je vidí (legacy podpora)
- Doporučuju ručně updatnout: `UPDATE campaigns SET user_id=1 WHERE user_id IS NULL`

---

## Soubory které se změnily:

### 1. **database/cold_calling_db.py**
- `_init_db()`: Přidán sloupec `user_id` 
- `create_campaign()`: Teď přijímá `user_id` parameter
- `get_campaigns()`: Filtruje podle `user_id`

### 2. **api/server.py**
- Import `sqlite3` přidán
- `/admin` route: Filtruje kampaně podle `session['user_id']`
- `/admin/create-campaign` route: Uloží `user_id` při vytvoření
- `/admin/campaign/<id>` route: **BEZPEČNOSTNÍ KONTROLA** - ověří že je to tvoje kampaň

---

## Bezpečnostní poznámky:

✅ Uživatel nemůže vidět kampaně jiných  
✅ Uživatel nemůže editovat/smazat cizí kampaň  
✅ Přímý URL hack neprůchodný (např. `/admin/campaign/999`)  
✅ Staré kampaně bez `user_id` jsou viditelné všem (legacy)

---

## Co dále?

1. **Testování** - Vytvoř 2 uživatele, ověř izolaci
2. **Starší data** - Ručně updatni kampaně bez `user_id`:
   ```sql
   UPDATE campaigns SET user_id = 1 WHERE user_id IS NULL;
   ```
3. **Ostatní resources** - Stejné řešení pro kontakty/hovory pokud chceš

---

**Hotovo!** 🎉

Jednotlivé uživatele jsou teď **izolované** v sociální izolaci. Každý vidí jen své!
