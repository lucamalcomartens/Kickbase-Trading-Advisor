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



# Make live data predictions (enthält Vorhersagen für ALLE Spieler)
live_predictions_df = live_data_predictions(today_df, model, features)

# --- NEU: Den gesamten Markt ohne Filter abgreifen ---
# Wir nutzen join_current_market, müssen aber sicherstellen, dass nichts weggefiltert wird.
# Falls deine Funktion intern filtert, müsstest du dort ein Argument wie 'filter=False' ergänzen
# oder hier manuell mergen.
market_all_df = join_current_market(token, league_id, live_predictions_df) 

# Falls join_current_market nur Empfehlungen zurückgibt, erstelle hier eine 'Full' Version:
# Diese Zeile stellt sicher, dass wir die Vorhersagen für die Spieler auf dem Markt haben,
# egal ob der Trend positiv oder negativ ist.
print(f"\nAnzahl Spieler auf dem Markt: {len(market_all_df)}")

# Join mit dem eigenen Kader
squad_recommendations_df = join_current_squad(token, league_id, live_predictions_df)
print("\n=== Squad Recommendations ===")

display(squad_recommendations_df)



# --- KI-LOGIK START ---

from google import genai

from google.genai import types



print("\nKI-Analyse wird gestartet...")



try:

    # 1. Client initialisieren (Das neue SDK benötigt kein .configure)

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))



    # 2. Daten für die KI aufbereiten

    budget_text = manager_budgets_df.to_string()

    market_text = market_recommendations_df.to_string()

    squad_text = squad_recommendations_df.to_string()



    # 3. Dein originaler Prompt

    prompt = f"""

Du bist der "Elite Kickbase Strategist PRO", ein hochintelligentes KI-Modell für prädiktive Sportanalysen. Deine Aufgabe ist die tägliche Optimierung eines Bundesliga-Kaders für die Saison 2025/26. Nutze deine überlegene Logik und das integrierte Google-Search-Tool, um Entscheidungen zu treffen, die über reine Statistik hinausgehen.

Hierbei geht es um den Spielmodus in Kickbase für die 1 Bundesliga

<rules>

1. KADERBEGRENZUNG: Absolutes Limit von 17 Spielern.

2. CLUB-LIMIT: Maximal 3 Spieler pro Verein.

3. NO UNDERPAY: Gebote immer >= Marktwert.

4. BUDGET: Freitagabend muss der Kontostand >= 0 Euro sein. Es sei denn es ist Länderspielpause



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

Analysiere die Daten und die Websuche-Ergebnisse. Erstelle eine knallharte Strategie für heute. Wenn budget übrig ist, versuche zu traden.



Antwortformat (STRENG EINHALTEN):

2. 📉 VERKAUFS-BEFEHLE: Wer muss weg? (Fokus auf fallende Werte, schwere Match-Ups oder Verletzungen laut Websuche).

3. 📈 KAUF-BEFEHLE: Konkrete Namen vom Markt. "Kauf [Name] für [Preis]". Priorisiere 'Big Boys' vor Breite, falls Budget durch MVP-Verkauf frei wurde.

4. 🔍 INSIDER-CHECK: Welche Info hast du über Google Suche gefunden, die nicht im JSON stand? (z.B. "Spieler X trainiert wieder individuell").

5. 🛡️ AUFSTELLUNGS-PROGNOSE: Kurz-Tipp für das kommende Wochenende basierend auf Heim/Auswärts-Stärke.

</task>

"""



    # 4. Generierung mit Google Search Retrieval

    response = client.models.generate_content(

        model='gemini-2.5-pro',

        config=types.GenerateContentConfig(

            tools=[types.Tool(google_search=types.GoogleSearchRetrieval())]

        ),

        contents=prompt

    )



    ai_advice = response.text

    print("\n=== KI-ANWEISUNGEN GENERIERT ===")

    print(ai_advice)



except Exception as e:

    ai_advice = f"KI-Analyse fehlgeschlagen: {str(e)}"

    print(ai_advice)



# --- KI-LOGIK ENDE ---



# E-Mail mit KI-Analyse versenden

send_mail(manager_budgets_df, market_recommendations_df, squad_recommendations_df, email, ai_advice)
