from features.predictions.predictions import live_data_predictions, join_current_market, join_current_squad

from features.predictions.preprocessing import preprocess_player_data, split_data

from features.predictions.modeling import train_model, evaluate_model

from kickbase_api.league import get_league_id
from kickbase_api.others import get_matchdays

from kickbase_api.user import login, get_budget, get_username

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
import time
from zoneinfo import ZoneInfo



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


def format_currency(value):
    """Format a numeric value for compact prompt output."""

    if pd.isna(value):
        return "n/a"
    return f"{float(value):,.0f}".replace(",", ".")


def format_prompt_table(df, columns, limit=None):
    """Return a compact table string with only the columns relevant for the prompt."""

    available_columns = [column for column in columns if column in df.columns]
    prompt_df = df[available_columns].copy()

    if limit is not None:
        prompt_df = prompt_df.head(limit)

    if prompt_df.empty:
        return "Keine Daten verfuegbar"

    return prompt_df.to_string(index=False)


def build_player_name(df):
    """Create a compact player name column from first and last name."""

    return (df["first_name"].fillna("") + " " + df["last_name"].fillna("")).str.strip()


def prepare_top_actions(market_df, squad_df):
    """Build compact top-action tables for the email header and mobile-first reading."""

    buy_now_df = market_df[market_df["buy_action"] == "buy_now"].copy().head(5)
    watchlist_df = market_df[
        (market_df["buy_action"] == "watchlist") & (~market_df["expiring_today"])
    ].copy().head(5)
    sell_df = squad_df[squad_df["squad_action"] == "sell"].copy().head(5)

    if not buy_now_df.empty:
        buy_now_df["Spieler"] = build_player_name(buy_now_df)
        buy_now_df = buy_now_df[["Spieler", "team_name", "asset_role", "priority_score", "bid_range"]].rename(
            columns={
                "team_name": "Team",
                "asset_role": "Rolle",
                "priority_score": "Score",
                "bid_range": "Gebot",
            }
        )

    if not watchlist_df.empty:
        watchlist_df["Spieler"] = build_player_name(watchlist_df)
        watchlist_df = watchlist_df[["Spieler", "team_name", "asset_role", "priority_score", "recommended_bid_max"]].rename(
            columns={
                "team_name": "Team",
                "asset_role": "Zieltyp",
                "priority_score": "Score",
                "recommended_bid_max": "Max Gebot",
            }
        )

    if not sell_df.empty:
        sell_df["Spieler"] = build_player_name(sell_df)
        sell_df = sell_df[["Spieler", "team_name", "squad_role", "sell_priority_score", "delta_prediction"]].rename(
            columns={
                "team_name": "Team",
                "squad_role": "Typ",
                "sell_priority_score": "Sell Score",
                "delta_prediction": "Delta",
            }
        )

    return {
        "Jetzt kaufen": {
            "subtitle": "Die wichtigsten Deals vor dem naechsten Marktwertupdate.",
            "data": buy_now_df,
        },
        "Spaeter beobachten": {
            "subtitle": "Starke Optionen, die nicht heute Nacht verloren gehen.",
            "data": watchlist_df,
        },
        "Eher verkaufen": {
            "subtitle": "Spieler, die Kapital blockieren oder an Risiko gewinnen.",
            "data": sell_df,
        },
    }


def get_next_matchday_context(token, competition_id):
    """Return basic schedule context for prompt steering around breaks and matchday pressure."""

    now = datetime.datetime.now(ZoneInfo("Europe/Berlin"))

    try:
        matchdays = get_matchdays(token, competition_id)
    except Exception:
        return {
            "next_matchday": "unbekannt",
            "next_matchday_date": "unbekannt",
            "days_until_next_matchday": "unbekannt",
            "trading_window_mode": "unknown",
            "friday_safety_mode": "unknown",
        }

    future_matchdays = []
    for matchday in matchdays:
        matchday_date = matchday.get("date")
        if not matchday_date:
            continue
        matchday_dt = datetime.datetime.fromisoformat(matchday_date).astimezone(ZoneInfo("Europe/Berlin"))
        if matchday_dt >= now:
            future_matchdays.append((matchday.get("day"), matchday_dt))

    if not future_matchdays:
        return {
            "next_matchday": "unbekannt",
            "next_matchday_date": "unbekannt",
            "days_until_next_matchday": "unbekannt",
            "trading_window_mode": "unknown",
            "friday_safety_mode": "unknown",
        }

    next_matchday, next_matchday_dt = future_matchdays[0]
    days_until_next_matchday = (next_matchday_dt.date() - now.date()).days

    if days_until_next_matchday >= 8:
        trading_window_mode = "extended_break"
    elif days_until_next_matchday >= 4:
        trading_window_mode = "normal_build_up"
    else:
        trading_window_mode = "matchday_close"

    friday_safety_mode = "active" if days_until_next_matchday <= 3 else "inactive"

    return {
        "next_matchday": next_matchday,
        "next_matchday_date": next_matchday_dt.strftime("%d-%m-%Y %H:%M"),
        "days_until_next_matchday": days_until_next_matchday,
        "trading_window_mode": trading_window_mode,
        "friday_safety_mode": friday_safety_mode,
    }



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

own_budget = get_budget(token, league_id)

own_username = get_username(token)

matchday_context = get_next_matchday_context(token, competition_ids[0])



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

# Pull the full current market without filtering to only positive predictions.
market_all_df = join_current_market(
    token,
    league_id,
    live_predictions_df,
    min_predicted_mv_target=None,
)

market_email_df = market_all_df[["last_name", "team_name", "mv", "mv_change_yesterday", "predicted_mv_change", "predicted_mv_target", "priority_score", "asset_role", "recommended_bid_max", "hours_to_exp", "expiring_today"]].copy()

print(f"\nAnzahl Spieler auf dem Markt: {len(market_all_df)}")

# Join mit dem eigenen Kader
squad_recommendations_df = join_current_squad(token, league_id, live_predictions_df)

squad_email_df = squad_recommendations_df[["last_name", "team_name", "mv", "mv_change_yesterday", "predicted_mv_change", "predicted_mv_target", "sell_priority_score", "squad_role", "s_11_prob"]].copy()

top_action_sections = prepare_top_actions(market_all_df, squad_recommendations_df)

print("\n=== Squad Recommendations ===")

display(squad_recommendations_df)



# --- KI-LOGIK START ---

from google import genai

from google.genai import types



print("\nKI-Analyse wird gestartet...")

MAX_AI_RETRIES = 3

RETRYABLE_AI_ERROR_MARKERS = [
    "503",
    "UNAVAILABLE",
    "high demand",
    "try again later",
]



try:

    # 1. Client initialisieren (Das neue SDK benötigt kein .configure)

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))



    # 2. Daten fuer die KI aufbereiten

    own_budget_row = manager_budgets_df[manager_budgets_df["User"] == own_username]
    own_available_budget = own_budget_row["Available Budget"].iloc[0] if not own_budget_row.empty else None
    squad_team_counts = squad_recommendations_df["team_name"].value_counts()
    squad_team_counts_text = squad_team_counts[squad_team_counts > 1].to_string() if not squad_team_counts.empty else "Keine auffaelligen Doppelungen"

    market_expiring_now_df = market_all_df[market_all_df["expiring_today"]].sort_values(
        ["priority_score", "delta_prediction", "hours_to_exp"],
        ascending=[False, False, True],
    )
    market_later_df = market_all_df[~market_all_df["expiring_today"]].sort_values(
        ["priority_score", "delta_prediction", "hours_to_exp"],
        ascending=[False, False, True],
    )
    market_trade_stash_df = market_all_df[
        (market_all_df["delta_prediction"] > 0) & (market_all_df["mv_change_yesterday"] <= 0)
    ].sort_values(["delta_prediction", "hours_to_exp"], ascending=[False, True])
    market_hold_df = market_all_df[
        (market_all_df["delta_prediction"] > 0)
        & (market_all_df["asset_role"].isin(["medium_term_hold", "core_starter"]))
    ].sort_values(["priority_score", "delta_prediction", "hours_to_exp"], ascending=[False, False, True])
    squad_risk_df = squad_recommendations_df.sort_values(["delta_prediction", "mv_change_yesterday"], ascending=[True, True])

    core_starter_count = int((squad_recommendations_df["squad_role"] == "core_starter").sum())
    rotation_hold_count = int((squad_recommendations_df["squad_role"] == "rotation_hold").sum())
    sell_candidate_count = int((squad_recommendations_df["squad_role"] == "sell_candidate").sum())

    squad_text = format_prompt_table(
        squad_recommendations_df,
        ["first_name", "last_name", "position", "team_name", "mv", "predicted_mv_change", "predicted_mv_target", "delta_prediction", "delta_percent", "s_11_prob", "football_signal_score", "sell_priority_score", "squad_role"],
        limit=18,
    )
    expiring_now_text = format_prompt_table(
        market_expiring_now_df,
        ["first_name", "last_name", "position", "team_name", "mv", "predicted_mv_change", "predicted_mv_target", "delta_prediction", "delta_percent", "priority_score", "football_signal_score", "asset_role", "buy_action", "recommended_bid_min", "recommended_bid_max", "hours_to_exp"],
        limit=18,
    )
    later_market_text = format_prompt_table(
        market_later_df,
        ["first_name", "last_name", "position", "team_name", "mv", "predicted_mv_change", "predicted_mv_target", "delta_prediction", "delta_percent", "priority_score", "football_signal_score", "asset_role", "buy_action", "recommended_bid_min", "recommended_bid_max", "hours_to_exp"],
        limit=18,
    )
    trade_stash_text = format_prompt_table(
        market_trade_stash_df,
        ["first_name", "last_name", "position", "team_name", "mv", "predicted_mv_change", "predicted_mv_target", "delta_prediction", "delta_percent", "priority_score", "asset_role", "recommended_bid_max", "hours_to_exp"],
        limit=12,
    )
    hold_candidates_text = format_prompt_table(
        market_hold_df,
        ["first_name", "last_name", "position", "team_name", "mv", "predicted_mv_change", "predicted_mv_target", "delta_prediction", "delta_percent", "priority_score", "football_signal_score", "asset_role", "recommended_bid_min", "recommended_bid_max", "hours_to_exp"],
        limit=12,
    )
    squad_risk_text = format_prompt_table(
        squad_risk_df,
        ["first_name", "last_name", "position", "team_name", "mv", "predicted_mv_change", "predicted_mv_target", "delta_prediction", "delta_percent", "s_11_prob", "football_signal_score", "sell_priority_score", "squad_action"],
        limit=12,
    )
    available_budget_text = format_currency(own_available_budget) if own_available_budget is not None else "n/a"
    own_budget_text = format_currency(own_budget)



    # 3. Prompt fuer eine expiry-aware und langfristige Trading-Strategie

    prompt = f"""

Du bist mein Kickbase Portfoliomanager fuer die 1. Bundesliga. Deine Aufgabe ist es, kurzfristige Marktwertgewinne bis zum naechsten Marktwertupdate mitzunehmen, ohne dabei die langfristige Trading-Strategie und die Kaderentwicklung aus den Augen zu verlieren.

<rules>

1. KADERBEGRENZUNG: Absolutes Limit von 17 Spielern.

2. CLUB-LIMIT: Maximal 3 Spieler pro Verein.

3. NO UNDERPAY: Gebote immer >= Marktwert.

4. BUDGET: Freitagabend muss der Kontostand >= 0 Euro sein, ausser in der Laenderspielpause.

5. ZEITFAKTOR: Spieler mit Ablauf vor dem naechsten Marktwertupdate haben hohe operative Prioritaet. Das ist aber nur ein Faktor und kein Automatismus.

6. LANGFRISTIGES TRADING: Beruecksichtige aktiv, ob ein Spieler ueber 2 bis 4 Tage oder bis zum naechsten Spieltag den besseren Gesamtertrag bringen kann als ein sofortiger Flip.

7. SPIELTAGS-READINESS: Wenn kein verlaengertes Tradingfenster vorliegt, muss bis Freitag vor dem Spieltag ein funktionierendes Team stehen und der Kontostand spaetestens dann >= 0 Euro sein.

</rules>



<grounding_instruction>

Nutze die Google Suche gezielt nur fuer die wichtigsten Entscheidungen.

- Pruefe die 5 wichtigsten Sofort-Kaufkandidaten, die vor dem naechsten Marktwertupdate auslaufen.

- Pruefe die 5 kritischsten Verkaufs- oder Halt-Entscheidungen in meinem Kader.

- Suche nur nach belastbaren Echtzeit-Infos wie Verletzungen, Trainingsstatus, Sperren, Rotationen oder Stammplatzverlust.

- Wenn du keine belastbare neue Information findest, sage das explizit und spekuliere nicht.

</grounding_instruction>



<current_data_context>

HEUTIGES DATUM: {today}

WOCHENTAG HEUTE: {datetime.datetime.now(ZoneInfo("Europe/Berlin")).strftime("%A")}

MEIN USERNAME: {own_username}

MEIN AKTUELLES BUDGET: {own_budget_text} Euro

MEIN GESCHAETZTES VERFUEGBARES BUDGET OHNE REGELVERSTOSS: {available_budget_text} Euro

AKTUELLE KADERGROESSE: {len(squad_recommendations_df)} von 17

NAECHSTER SPIELTAG: {matchday_context['next_matchday']}

NAECHSTER SPIELTAG STARTET: {matchday_context['next_matchday_date']}

TAGE BIS ZUM NAECHSTEN SPIELTAG: {matchday_context['days_until_next_matchday']}

TRADING_WINDOW_MODE: {matchday_context['trading_window_mode']}

FRIDAY_SAFETY_MODE: {matchday_context['friday_safety_mode']}

KADERSTRUKTUR: {core_starter_count} core_starter, {rotation_hold_count} rotation_hold, {sell_candidate_count} sell_candidate

MEHRFACHBELEGUNG PRO VEREIN IM KADER:
{squad_team_counts_text}

MEIN KADER:
{squad_text}

MARKTSEGMENT A - SPIELER, DIE VOR DEM NAECHSTEN MARKTWERTUPDATE ABLAUFEN:
{expiring_now_text}

MARKTSEGMENT B - SPIELER, DIE SPAETER ABLAUFEN:
{later_market_text}

MARKTSEGMENT C - MOEGLICHE TRADING-REBOUNDS (gestern schwach, Modell heute positiv):
{trade_stash_text}

MARKTSEGMENT D - POSITIVE HOLDS FUER 2 BIS 4 TAGE ODER BIS ZUM SPIELTAG:
{hold_candidates_text}

KADER-RISIKEN AUS MODELLSICHT:
{squad_risk_text}

HINWEIS ZU DEN SCORES:
- priority_score bewertet Dringlichkeit, Marktwertpotenzial, Trend, Startelfwahrscheinlichkeit und interne Fussballsignale.
- football_signal_score ist ein interner Struktur-Score aus Startelfwahrscheinlichkeit, Punkten, Minuten, Punkte-pro-Minute und Naehe zum naechsten Spiel.
- predicted_mv_change ist die erwartete Marktwertveraenderung bis morgen. predicted_mv_target ist der daraus abgeleitete absolute Marktwert fuer morgen.
- recommended_bid_min und recommended_bid_max sind bereits berechnete Fallback-Gebote aus Score, Ablaufzeit und erwarteter Marktwertchance.

</current_data_context>



<task>

Erstelle eine konkrete Abendstrategie fuer mein Kickbase-Team.

- Priorisiere zuerst Spieler aus Marktsegment A, wenn sie bis zum naechsten Marktwertupdate die beste Kombination aus Zeitfaktor, Trading-Potenzial und sportlicher Relevanz haben.

- Vernachlaessige Marktsegment B nicht. Wenn spaeter auslaufende Spieler strategisch deutlich besser sind als die Sofort-Kandidaten, sollst du das klar sagen.

- Denke wie ein Trader und wie ein Manager: kurzfristige Gewinne mitnehmen, aber nicht blind alles auf den naechsten Tag optimieren, wenn ein Halten ueber 2 bis 4 Tage oder bis zum naechsten Spieltag den besseren Gesamtertrag verspricht.

- Bewerte fuer gute Kaufkandidaten immer explizit, ob der bessere Plan ist: Overnight-Flip, 2-bis-4-Tage-Hold oder Kaderbaustein bis zum Spieltag.

- Wenn TRADING_WINDOW_MODE = extended_break, nutze die zusaetzliche Zeit aktiv. In solchen Phasen darfst du Spieler staerker nach mehrtaegigem Trading-Potenzial statt nur nach naechstem Update bewerten.

- Wenn FRIDAY_SAFETY_MODE = active, priorisiere Spieltags-Readiness: bis Freitag muss ein funktionierendes Team stehen und das Budget spaetestens dann >= 0 sein, ausser es liegt wirklich ein verlaengertes Tradingfenster ohne direkten Spieltag vor.

- Nutze die vorhandenen priority_score-, asset_role- und recommended_bid-Werte aktiv als Grundlage. Du darfst sie begruendet leicht anpassen, sollst sie aber nicht ignorieren.

- Gib fuer jeden Kaufkandidaten ein maximales Gebot in Euro an. Das Gebot soll sich an Wichtigkeit, Budget, Trading-Chance, Startelf-Wahrscheinlichkeit und Ablaufzeit orientieren.

- Unterscheide klar zwischen:
  A) Sofort kaufen vor dem naechsten Marktwertupdate
  B) Beobachten und spaeter angreifen
  C) Nicht kaufen

- Beruecksichtige auch Verkaeufe aus meinem Kader, wenn dadurch bessere Trades oder wichtigere Einkaeufe moeglich werden.

- Wenn ein Spieler vor allem als Trading-Asset interessant ist, sage das explizit.



Antwortformat (STRENG EINHALTEN):

1. TEAMSTATUS: Kurze Einordnung meines Kaders, meines Budgets, des Tradingfensters und meines dringendsten Handlungsbedarfs heute Abend.

2. VERKAUFS-BEFEHLE: Wer muss weg oder ist aktiv entbehrlich? Fokus auf fallende Werte, Risiko und Kapitalfreisetzung.

3. SOFORT-KAEUFE BIS ZUM NAECHSTEN UPDATE: Nenne nur die wichtigsten Spieler aus Marktsegment A. Format je Spieler: "Kauf [Name] | Prioritaet [A/B/C] | Max Gebot [Euro] | Rolle [Starter/Trader/Hold] | Warum jetzt".

4. SPAETERE CHANCEN UND HOLDS: Welche spaeter auslaufenden Spieler oder mehrtaegigen Holds darf ich nicht verpassen? Format je Spieler: "Beobachte [Name] | Zielstrategie [Overnight/2-4 Tage/Spieltag] | Spaeteres Max Gebot | Warum relevant".

5. NEWS-CHECK: Welche belastbaren Infos aus der Websuche veraendern die Entscheidung wirklich?

6. TRADING-PLAN: Was ist deine Strategie fuer die naechsten 2 bis 4 Tage, damit ich nicht nur heute, sondern auch langfristig besser trade?

7. FRIDAY-CHECK: Was muss bis Freitag vor dem Spieltag unbedingt erledigt sein, damit ich nicht im Minus bin und ein funktionierendes Team habe?

</task>

"""



    # 4. Generierung mit Google Search Retrieval

    response = None
    last_error = None

    for attempt in range(1, MAX_AI_RETRIES + 1):
        try:
            response = client.models.generate_content(

                model='gemini-2.5-pro',

                config=types.GenerateContentConfig(

                    tools=[types.Tool(google_search=types.GoogleSearchRetrieval())]

                ),

                contents=prompt

            )
            break
        except Exception as error:
            last_error = error
            error_text = str(error)
            is_retryable = any(marker.lower() in error_text.lower() for marker in RETRYABLE_AI_ERROR_MARKERS)

            if attempt == MAX_AI_RETRIES or not is_retryable:
                raise

            wait_seconds = attempt * 5
            print(f"KI-Analyse Versuch {attempt} fehlgeschlagen ({error_text}). Neuer Versuch in {wait_seconds} Sekunden...")
            time.sleep(wait_seconds)

    if response is None and last_error is not None:
        raise last_error



    ai_advice = response.text

    print("\n=== KI-ANWEISUNGEN GENERIERT ===")

    print(ai_advice)



except Exception as e:

    ai_advice = f"KI-Analyse fehlgeschlagen: {str(e)}"

    print(ai_advice)



# --- KI-LOGIK ENDE ---



# E-Mail mit KI-Analyse versenden

send_mail(manager_budgets_df, market_email_df, squad_email_df, email, ai_advice, top_action_sections)
