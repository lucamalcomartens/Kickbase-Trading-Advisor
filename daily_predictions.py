from __future__ import annotations

import datetime
import os

import google.genai as genai
from dotenv import load_dotenv
from IPython.display import display

from features.ai_advisor import generate_ai_advice
from features.advisor_db import (
    create_advisor_tables,
    load_offer_tracking_summary,
    reconcile_tracked_market_offers,
    save_run_snapshot,
    upsert_current_market_offers,
)
from features.analysis_support import (
    build_history_entry,
    get_next_matchday_context,
    load_analysis_history,
    prepare_top_actions,
    save_analysis_history,
)
from features.bid_history import apply_personal_bid_tuning, build_transfer_history_df, enrich_market_with_bid_history
from features.budgets import calc_manager_budgets
from features.notifier import send_mail
from features.offer_tracking import extract_current_market_offers, summarize_market_feed_debug, summarize_offer_feed_debug
from features.strategy_engine import build_strategy_context
from features.predictions.data_handler import (
    check_if_data_reload_needed,
    create_player_data_table,
    load_player_data_from_db,
    save_player_data_to_db,
)
from features.predictions.modeling import evaluate_model, train_model
from features.predictions.predictions import (
    join_current_market,
    join_current_squad,
    live_data_predictions,
)
from features.predictions.preprocessing import preprocess_player_data, split_data
from features.run_report import write_run_report
from kickbase_api.league import get_league_id, get_league_market_raw
from kickbase_api.manager import get_manager_transfer_feed, get_managers
from kickbase_api.others import enrich_with_fixture_context, get_fixture_context
from kickbase_api.user import get_budget, get_username, login
from project_settings import SystemSettings, configure_display, load_user_settings


def main() -> None:
    load_dotenv()
    configure_display()

    print(f"GenAI Version: {genai.__version__}")

    system_settings = SystemSettings()
    user_settings = load_user_settings()
    report_date = datetime.date.today().strftime("%d. %B %Y")

    create_advisor_tables(system_settings.database_path)

    username = os.getenv("KICK_USER")
    password = os.getenv("KICK_PASS")

    token = login(username, password)
    print("\nLogged in to Kickbase.")

    league_id = get_league_id(token, user_settings.league_name)

    manager_budgets_df = calc_manager_budgets(
        token,
        league_id,
        user_settings.league_start_date,
        user_settings.start_budget,
    )
    print("\n=== Manager Budgets ===")
    display(manager_budgets_df)

    own_budget = get_budget(token, league_id)
    own_username = get_username(token)
    manager_lookup = dict(get_managers(token, league_id))
    own_manager_id = manager_lookup.get(own_username)
    matchday_context = get_next_matchday_context(token, user_settings.competition_ids[0])
    analysis_history = load_analysis_history(system_settings.analysis_history_path)

    create_player_data_table(system_settings.database_path)
    reload_data = check_if_data_reload_needed(system_settings.database_path)
    save_player_data_to_db(
        token,
        user_settings.competition_ids,
        system_settings.last_mv_values,
        system_settings.last_pfm_values,
        reload_data,
        system_settings.database_path,
    )
    player_df = load_player_data_from_db(system_settings.database_path)
    print("\nData loaded from database.")

    processed_player_df, today_df = preprocess_player_data(player_df)
    X_train, X_test, y_train, y_test = split_data(
        processed_player_df,
        system_settings.features,
        system_settings.target,
    )
    print("\nData preprocessed.")

    model = train_model(X_train, y_train)
    signs_percent, rmse, mae, r2 = evaluate_model(model, X_test, y_test)
    model_metrics = {
        "signs_percent": round(float(signs_percent), 2),
        "rmse": round(float(rmse), 2),
        "mae": round(float(mae), 2),
        "r2": round(float(r2), 4),
    }
    print(
        f"\nModel evaluation:\nSigns correct: {signs_percent:.2f}%\nRMSE: {rmse:.2f}\nMAE: {mae:.2f}\nR2: {r2:.2f}"
    )

    live_predictions_df = live_data_predictions(today_df, model, system_settings.features)
    fixture_context = get_fixture_context(user_settings.competition_ids[0])
    transfer_history_df = build_transfer_history_df(
        token,
        league_id,
        user_settings.league_start_date,
        live_predictions_df,
        system_settings.database_path,
    )

    raw_market_feed = get_league_market_raw(token, league_id)

    offer_tracking_summary = {"counts": {}, "recent_outbid": [], "recent_active": [], "debug": {}, "market_debug": {}}
    if own_manager_id is not None:
        try:
            raw_transfer_feed = get_manager_transfer_feed(token, league_id, own_manager_id)
            current_offers_df = extract_current_market_offers(raw_market_feed, league_id, own_username)
            upsert_current_market_offers(current_offers_df, system_settings.database_path)
            reconcile_tracked_market_offers(
                system_settings.database_path,
                league_id,
                own_username,
                current_offers_df,
                transfer_history_df,
            )
            offer_tracking_summary = load_offer_tracking_summary(
                system_settings.database_path,
                league_id,
                own_username,
            )
            if offer_tracking_summary["counts"].get("active_offers", 0) == 0:
                offer_tracking_summary["debug"] = summarize_offer_feed_debug(raw_transfer_feed)
                offer_tracking_summary["market_debug"] = summarize_market_feed_debug(
                    raw_market_feed,
                    target_player_names=["Péter Gulácsi", "Peter Gulacsi", "Gulácsi", "Gulacsi"],
                )
            else:
                offer_tracking_summary["market_debug"] = summarize_market_feed_debug(
                    raw_market_feed,
                    target_player_names=["Péter Gulácsi", "Peter Gulacsi", "Gulácsi", "Gulacsi"],
                )
            print(
                f"\nOffer-Tracking: {offer_tracking_summary['counts'].get('active_offers', 0)} aktiv, "
                f"{offer_tracking_summary['counts'].get('outbid_offers', 0)} ueberboten, "
                f"{offer_tracking_summary['counts'].get('won_offers', 0)} gewonnen"
            )
        except Exception as error:
            print(f"Warnung: Offer-Tracking konnte nicht geladen werden: {error}")

    market_all_df = join_current_market(
        token,
        league_id,
        live_predictions_df,
        min_predicted_mv_target=None,
    )
    market_all_df = enrich_market_with_bid_history(market_all_df, transfer_history_df)
    market_all_df = apply_personal_bid_tuning(market_all_df, offer_tracking_summary)
    market_all_df = enrich_with_fixture_context(market_all_df, fixture_context)
    market_all_df, strategy_context = build_strategy_context(market_all_df, offer_tracking_summary, own_budget)
    market_email_df = market_all_df[
        [
            "last_name",
            "team_name",
            "mv",
            "mv_change_yesterday",
            "predicted_mv_change",
            "predicted_mv_target",
            "priority_score",
            "asset_role",
            "recommended_bid_max",
            "competitive_bid_max",
            "recent_bid_competition",
            "bid_strategy_note",
            "active_offer_decision",
            "active_offer_recommended_new_bid",
            "hours_to_exp",
            "expiring_today",
            "next_opponent",
            "home_or_away",
            "fixture_difficulty",
        ]
    ].copy()
    print(f"\nAnzahl Spieler auf dem Markt: {len(market_all_df)}")

    squad_recommendations_df = join_current_squad(token, league_id, live_predictions_df)
    squad_recommendations_df = enrich_with_fixture_context(squad_recommendations_df, fixture_context)
    squad_email_df = squad_recommendations_df[
        [
            "last_name",
            "team_name",
            "mv",
            "mv_change_yesterday",
            "predicted_mv_change",
            "predicted_mv_target",
            "sell_priority_score",
            "squad_role",
            "s_11_prob",
            "next_opponent",
            "home_or_away",
            "fixture_difficulty",
        ]
    ].copy()
    top_action_sections = prepare_top_actions(market_all_df, squad_recommendations_df, strategy_context=strategy_context)
    print("\n=== Squad Recommendations ===")
    display(squad_recommendations_df)

    print("\nKI-Analyse wird gestartet...")
    ai_status = "not_started"

    try:
        ai_advice, ai_status = generate_ai_advice(
            manager_budgets_df=manager_budgets_df,
            market_all_df=market_all_df,
            squad_recommendations_df=squad_recommendations_df,
            strategy_context=strategy_context,
            own_username=own_username,
            own_budget=own_budget,
            report_date=report_date,
            matchday_context=matchday_context,
            analysis_history=analysis_history,
            fixture_context_active=bool(fixture_context),
        )

        history_entry = build_history_entry(
            report_date,
            own_budget,
            matchday_context,
            market_all_df,
            squad_recommendations_df,
            ai_advice,
            ai_status,
            strategy_context=strategy_context,
        )
        analysis_history.append(history_entry)
        save_analysis_history(system_settings.analysis_history_path, analysis_history)

        print("\n=== KI-ANWEISUNGEN GENERIERT ===")
        print(ai_advice)
    except Exception as error:
        ai_advice = f"KI-Analyse fehlgeschlagen: {error}"
        ai_status = "failed"

        history_entry = build_history_entry(
            report_date,
            own_budget,
            matchday_context,
            market_all_df,
            squad_recommendations_df,
            ai_advice,
            ai_status,
            strategy_context=strategy_context,
        )
        analysis_history.append(history_entry)
        save_analysis_history(system_settings.analysis_history_path, analysis_history)

        print(ai_advice)

    mail_status = "skipped" if not user_settings.email else "success"
    try:
        send_mail(
            manager_budgets_df,
            market_email_df,
            squad_email_df,
            user_settings.email,
            ai_advice,
            top_action_sections,
        )
    except Exception as error:
        mail_status = f"failed: {error}"
        print(f"Warnung: E-Mail-Versand fehlgeschlagen: {error}")

    save_run_snapshot(
        db_path=system_settings.database_path,
        report_date=report_date,
        league_id=league_id,
        own_username=own_username,
        own_budget=own_budget,
        matchday_context=matchday_context,
        model_metrics=model_metrics,
        ai_status=ai_status,
        mail_status=mail_status,
        manager_budgets_df=manager_budgets_df,
        market_df=market_all_df,
        squad_df=squad_recommendations_df,
    )

    write_run_report(
        output_dir=system_settings.run_output_dir,
        repo_output_dir=system_settings.repo_reports_dir,
        report_date=report_date,
        own_username=own_username,
        own_budget=own_budget,
        manager_budgets_df=manager_budgets_df,
        matchday_context=matchday_context,
        model_metrics=model_metrics,
        market_df=market_all_df,
        squad_df=squad_recommendations_df,
        ai_status=ai_status,
        ai_advice=ai_advice,
        mail_status=mail_status,
        fixture_context_active=bool(fixture_context),
        offer_tracking_summary=offer_tracking_summary,
        strategy_context=strategy_context,
    )


if __name__ == "__main__":
    main()
