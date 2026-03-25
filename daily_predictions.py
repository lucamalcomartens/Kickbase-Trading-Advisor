from features.predictions.predictions import live_data_predictions, join_current_market, join_current_squad
from features.predictions.preprocessing import preprocess_player_data, split_data
from features.predictions.modeling import train_model, evaluate_model
from kickbase_api.league import get_league_id
from kickbase_api.user import login
from features.notifier import send_mail
import datetime
import google.genai as genai
from features.predictions.data_handler import (
    create_player_data_table,
    check_if_data_reload_needed,
    save_player_data_to_db,
    load_player_data_from_db,
)
from features.budgets import calc_manager_budgets
from IPython.display import display
from dotenv import load_dotenv
import os, pandas as pd

# Load environment variables from .env file
load_dotenv() 

print(f"GenAI Version: {genai.__version__}")

# ----------------- Notes & TODOs -----------------

# TODO Fix the UTC timezone problems in the github actions scheduling
# TODO Add prediction of 3, 7 days, to give more context
# TODO Based upon the overpay of the other users, calculate a max price to pay for a player
# TODO Add features like starting 11 probability, injuries, ...
# TODO Improve budget calculation, weird bug that for me the budgets is 513929 off, idk why, checked everything

# ----------------- SYSTEM PARAMETERS -----------------
# Should be left unchanged unless you know what you're doing

last_mv_values = 365    # in days, max 365
last_pfm_values = 50    # in matchdays, max idk

# which features to use for training and prediction
features = [
    "p", "mv", "days_to_next", 
    "mv_change_1d", "mv_trend_1d", 
    "mv_change_3d", "mv_vol_3d",
    "mv_trend_7d", "market_divergence"
]

today = datetime.date.today().strftime("%d. %B %Y")

# what column to learn and predict on
target = "mv_target_clipped"

# Set dot as thousands separator for better readability
pd.options.display.float_format = lambda x: '{:,.0f}'.format(x).replace(',', '.')

# Show all columns when displaying dataframes
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)

# ----------------- USER SETTINGS -----------------
# Adjust these settings to your preferences

competition_ids = [1]                   # 1 = Bundesliga, 2 = 2. Bundesliga, 3 = La Liga
league_name = "Spitz"  # Name of your league, must be exact match, can be done via env or hardcoded
start_budget = 50_000_000               # Starting budget of your league, used to calculate current budgets of other managers
league_start_date = "2025-12-22"        # Start date of your league, used to filter activities, format: YYYY-MM-DD
email = os.getenv("EMAIL_USER")         # Email to send recommendations to, can be the same as EMAIL_USER or different

# ---------------------------------------------------

# Load environment variables and login to kickbase
USERNAME = os.getenv("KICK_USER") # DO NOT CHANGE THIS, YOU MUST SET THOSE IN GITHUB SECRETS OR A .env FILE
PASSWORD = os.getenv("KICK_PASS") # DO NOT CHANGE THIS, YOU MUST SET THOSE IN GITHUB SECRETS OR A .env FILE
token = login(USERNAME, PASSWORD)
print("\nLogged in to Kickbase.")

# Get league ID
league_id = get_league_id(token, league_name)

# Calculate (estimated) budgets of all managers in the league
manager_budgets_df = calc_manager_budgets(token, league_id, league_start_date, start_budget)
print("\n=== Manager Budgets ===")
display(manager_budgets_df)

# Data handling
create_player_data_table()
reload_data = check_if_data_reload_needed()
save_player_data_to_db(token, competition_ids, last_mv_values, last_pfm_values, reload_data)
player_df = load_player_data_from_db()
print("\nData loaded from database.")

# Preprocess the data and spit the data
proc_player_df, today_df = preprocess_player_data(player_df)
X_train, X_test, y_train, y_test = split_data(proc_player_df, features, target)
print("\nData preprocessed.")

# Train and evaluate the model
model = train_model(X_train, y_train)
signs_percent, rmse, mae, r2 = evaluate_model(model, X_test, y_test)
print(f"\nModel evaluation:\nSigns correct: {signs_percent:.2f}%\nRMSE: {rmse:.2f}\nMAE: {mae:.2f}\nR2: {r2:.2f}")

# Make live data predictions
live_predictions_df = live_data_predictions(today_df, model, features)

# Join with current available players on the market
market_recommendations_df = join_current_market(token, league_id, live_predictions_df)
print("\n=== Market Recommendations ===")
display(market_recommendations_df)

# Join with current players on the team
squad_recommendations_df = join_current_squad(token, league_id, live_predictions_df)
print("\n=== Squad Recommendations ===")
display(squad_recommendations_df)

# --- KI-LOGIK START ---
print("\nKI-Analyse wird gestartet...")


# KI konfigurieren
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name='gemini-2.5-pro',
    tools=[
        {"google_search": {}}
    ]
)

# Daten für die KI aufbereiten
budget_text = manager_budgets_df.to_string()
market_text = market_recommendations_df.to_string()
squad_text = squad_recommendations_df.to_string()

# DER RADIKALE PROFI-PROMPT
prompt = f"""
Du bist der "Elite Kickbase Strategist PRO", ein hochintelligentes KI-Modell für prädiktive Sportanalysen. Deine Aufgabe ist die tägliche Optimierung eines Bundesliga-Kaders für die Saison 2025/26. Nutze deine überlegene Logik und das integrierte Google-Search-Tool, um Entscheidungen zu treffen, die über reine Statistik hinausgehen.

<rules>
1. KADERBEGRENZUNG: Absolutes Limit von 17 Spielern.
2. CLUB-LIMIT: Maximal 3 Spieler pro Verein.
3. NO UNDERPAY: Gebote immer >= Marktwert.
4. MVP-LIQUIDATION: Verkaufe zwingend den punktbesten Spieler des letzten Spieltags (MVP).
5. BUDGET: Freitagabend muss der Kontostand >= 0 Euro sein.
</rules>

<grounding_instruction>
Nutze die Google Suche aktiv, um folgende Echtzeit-Informationen zu prüfen, bevor du eine Empfehlung abgibst:
- Aktuelle Verletzungen oder Trainingsabbrüche der letzten 24 Stunden für Spieler in meinem Kader oder auf dem Markt.
- Voraussichtliche Rotationen bei Top-Teams (Bayern, Dortmund, Leipzig) aufgrund von Champions-League-Belastung.
- Marktwert-Trends: Bestätige, ob der Trend eines Spielers (UP/DOWN) durch reale News (z.B. Stammplatzverlust) untermauert wird.
</grounding_instruction>

<current_data_context>
HEUTIGES DATUM: {today}

DATEN:
BUDGETS: {budget_text}
MARKT: {market_text}
KADER: {squad_text}
</current_data_context>

<task>
Analysiere die Daten und die Websuche-Ergebnisse. Erstelle eine knallharte Strategie für heute.

Antwortformat (STRENG EINHALTEN):
1. 🚨 PFLICHT-AKTIONEN: MVP-Verkauf (Name + Preis) & Regelverstöße.
2. 📉 VERKAUFS-BEFEHLE: Wer muss weg? (Fokus auf fallende Werte, schwere Match-Ups oder Verletzungen laut Websuche).
3. 📈 KAUF-BEFEHLE: Konkrete Namen vom Markt. "Kauf [Name] für [Preis]". Priorisiere 'Big Boys' vor Breite, falls Budget durch MVP-Verkauf frei wurde.
4. 🔍 INSIDER-CHECK: Welche Info hast du über Google Suche gefunden, die nicht im JSON stand? (z.B. "Spieler X trainiert wieder individuell").
5. 🛡️ AUFSTELLUNGS-PROGNOSE: Kurz-Tipp für das kommende Wochenende basierend auf Heim/Auswärts-Stärke.
</task>


"""

try:
    # Generierung der Antwort
    response = model.generate_content(prompt)
    ai_advice = response.text
    print("\n=== KI-ANWEISUNGEN GENERIERT ===")
    print(ai_advice)
except Exception as e:
    ai_advice = f"KI-Analyse fehlgeschlagen: {str(e)}"
    print(ai_advice)

# --- KI-LOGIK ENDE ---

# E-Mail mit KI-Analyse versenden
send_mail(manager_budgets_df, market_recommendations_df, squad_recommendations_df, email, ai_advice)
