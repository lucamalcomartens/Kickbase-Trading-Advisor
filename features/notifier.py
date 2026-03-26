from datetime import datetime, timedelta
from email.message import EmailMessage
from zoneinfo import ZoneInfo
from html import escape
import smtplib
import os

def send_mail(budget_df, market_df, squad_df, email, ai_advice=None, top_action_sections=None):
    """Sends an email with the provided DataFrames as HTML tables and AI advice."""

    if not email:
        print("\nNo email provided, skipping email sending.")
        return

    EMAIL_ADDRESS = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

    # Zeitberechnung für den Betreff
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    date_to_show = now + timedelta(days=1) if now.hour >= 22 else now
    today = date_to_show.strftime("%d-%m-%Y")

    # Metadata
    msg = EmailMessage()
    msg["Subject"] = f"Kickbase Analyse: {today}"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email

    def format_value(value):
        if value is None:
            return "-"

        if isinstance(value, bool):
            if value:
                return '<span style="display:inline-block;padding:4px 10px;border-radius:999px;background:#fff1f1;color:#9f1c1c;font-size:12px;font-weight:700;">Heute faellig</span>'
            return '<span style="display:inline-block;padding:4px 10px;border-radius:999px;background:#eef7ee;color:#1f6f43;font-size:12px;font-weight:700;">Spaeter</span>'

        if isinstance(value, float):
            if value.is_integer():
                return f"{int(value):,}".replace(",", ".")
            return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        if isinstance(value, int):
            return f"{value:,}".replace(",", ".")

        return escape(str(value))

    def cell_style(column_name, value):
        style = "padding:12px 14px;border-bottom:1px solid #e7ecf3;font-size:13px;color:#203040;vertical-align:top;"
        right_aligned_columns = {"mv", "budget", "mv_change_yesterday", "predicted_mv_change", "predicted_mv_target", "s_11_prob", "hours_to_exp", "priority_score", "recommended_bid_max", "sell_priority_score", "Score", "Sell Score", "Delta", "Max Gebot"}
        if column_name in right_aligned_columns:
            style += "text-align:right;font-variant-numeric:tabular-nums;"

        if column_name in {"mv_change_yesterday", "predicted_mv_change", "predicted_mv_target", "budget", "Delta"} and isinstance(value, (int, float)):
            if value > 0:
                style += "color:#1f6f43;font-weight:700;"
            elif value < 0:
                style += "color:#9f1c1c;font-weight:700;"

        return style

    def style_df(df):
        if df.empty:
            return """
            <div style="padding:18px 20px;border:1px dashed #c9d3e0;border-radius:14px;background:#f8fafc;color:#516173;font-size:14px;">
                Keine Daten verfuegbar.
            </div>
            """

        header_cells = "".join(
            f'<th style="padding:12px 14px;background:#14324a;color:#f4f8fb;text-align:left;font-size:12px;letter-spacing:0.04em;text-transform:uppercase;border-bottom:1px solid #274760;">{escape(str(column))}</th>'
            for column in df.columns
        )

        body_rows = []
        for index, row in enumerate(df.itertuples(index=False, name=None)):
            row_background = "#ffffff" if index % 2 == 0 else "#f7fafc"
            cells = "".join(
                f'<td style="{cell_style(column_name, value)}">{format_value(value)}</td>'
                for column_name, value in zip(df.columns, row)
            )
            body_rows.append(f'<tr style="background:{row_background};">{cells}</tr>')

        return f"""
        <table style="width:100%;border-collapse:separate;border-spacing:0;overflow:hidden;border:1px solid #d9e2ec;border-radius:16px;background:#ffffff;">
            <thead>
                <tr>{header_cells}</tr>
            </thead>
            <tbody>
                {''.join(body_rows)}
            </tbody>
        </table>
        """

    def section_block(title, subtitle, table_html):
        return f"""
        <div style="margin-top:28px;padding:24px;background:#ffffff;border:1px solid #dfe7f0;border-radius:20px;box-shadow:0 10px 30px rgba(20, 50, 74, 0.06);">
            <h3 style="margin:0 0 8px 0;font-size:20px;line-height:1.2;color:#102a43;">{title}</h3>
            <p style="margin:0 0 18px 0;font-size:14px;line-height:1.5;color:#52606d;">{subtitle}</p>
            {table_html}
        </div>
        """

    def top_action_block(title, subtitle, df):
        return f"""
        <div style="margin-top:16px;padding:18px;background:#ffffff;border:1px solid #dfe7f0;border-radius:18px;box-shadow:0 8px 24px rgba(20, 50, 74, 0.05);">
            <div style="font-size:12px;letter-spacing:0.08em;text-transform:uppercase;color:#627d98;">Top Entscheidung</div>
            <h4 style="margin:6px 0 6px 0;font-size:18px;line-height:1.2;color:#102a43;">{title}</h4>
            <p style="margin:0 0 14px 0;font-size:13px;line-height:1.5;color:#52606d;">{subtitle}</p>
            {style_df(df)}
        </div>
        """

    def stat_card(label, value, accent_color, background_color):
        return f"""
        <div style="display:inline-block;width:31%;min-width:180px;margin:0 1% 12px 1%;vertical-align:top;">
            <div style="padding:18px 18px 16px 18px;border-radius:18px;background:{background_color};border:1px solid rgba(16, 42, 67, 0.08);">
                <div style="font-size:12px;letter-spacing:0.06em;text-transform:uppercase;color:#486581;">{label}</div>
                <div style="margin-top:8px;font-size:28px;font-weight:700;line-height:1;color:{accent_color};">{value}</div>
            </div>
        </div>
        """

    # Vorbereitung der KI-Sektion (Nur wenn ai_advice vorhanden ist)
    ai_section = ""
    if ai_advice:
        ai_section = f"""
        <div style="margin-top:28px;padding:24px 26px;border-radius:20px;background:#14324a;color:#f4f8fb;box-shadow:0 14px 36px rgba(20, 50, 74, 0.18);">
            <div style="font-size:12px;letter-spacing:0.08em;text-transform:uppercase;color:#9fbad0;">KI Analyse</div>
            <h3 style="margin:10px 0 12px 0;font-size:24px;line-height:1.2;color:#ffffff;">Dein KI-Berater empfiehlt</h3>
            <p style="margin:0;white-space:pre-wrap;font-size:15px;line-height:1.7;color:#e6edf3;">
                {escape(ai_advice)}
            </p>
        </div>
        """

    buy_now_count = 0
    sell_count = 0
    if top_action_sections:
        buy_now_count = len(top_action_sections.get("Jetzt kaufen", {}).get("data", []))
        sell_count = len(top_action_sections.get("Eher verkaufen", {}).get("data", []))

    summary_cards = "".join([
        stat_card("Marktspieler", len(market_df), "#9f1c1c", "#fff4eb"),
        stat_card("Kaderspieler", len(squad_df), "#1d4f91", "#edf4ff"),
        stat_card("Sofortaktionen", buy_now_count + sell_count, "#1f6f43", "#eef7ee"),
    ])

    top_actions_section = ""
    if top_action_sections:
        blocks = []
        for title, section in top_action_sections.items():
            blocks.append(top_action_block(title, section.get("subtitle", ""), section.get("data")))
        top_actions_section = f"""
        <div style="margin-top:28px;padding:24px;background:linear-gradient(180deg, #f8fbff 0%, #eef4fb 100%);border:1px solid #d6e2f0;border-radius:22px;">
            <div style="font-size:12px;letter-spacing:0.1em;text-transform:uppercase;color:#486581;">Heute Abend zuerst lesen</div>
            <h3 style="margin:8px 0 6px 0;font-size:24px;line-height:1.2;color:#102a43;">Top Aktionen</h3>
            <p style="margin:0 0 8px 0;font-size:14px;line-height:1.5;color:#52606d;">Die wichtigsten Entscheidungen stehen vor den Detailtabellen, damit du auf dem Handy direkt weisst, was jetzt zu tun ist.</p>
            {''.join(blocks)}
        </div>
        """

    market_section = section_block(
        "Transfermarkt Uebersicht",
        "Alle Spieler, die aktuell auf dem Markt sind, inklusive erwarteter Veraenderung und prognostiziertem Marktwert fuer morgen.",
        style_df(market_df),
    )
    squad_section = section_block(
        "Dein Kader",
        "Status, erwartete Veraenderung und Prognose fuer deine aktuellen Spieler.",
        style_df(squad_df),
    )

    # E-Mail Inhalt zusammenbauen
    msg.set_content("Ergebnisse sind nur in der HTML-Ansicht sichtbar.", subtype="plain")
    msg.add_alternative(f"""\
    <html>
    <body style="margin:0;padding:0;background:#eaf1f7;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;color:#102a43;">
        <div style="padding:28px 16px;">
            <div style="max-width:1040px;margin:0 auto;">
                <div style="padding:34px 32px;border-radius:28px;background:linear-gradient(135deg, #102a43 0%, #1f4f74 100%);color:#ffffff;box-shadow:0 18px 40px rgba(16, 42, 67, 0.18);">
                    <div style="font-size:12px;letter-spacing:0.12em;text-transform:uppercase;color:#a9c1d4;">KickAdvisor Daily Report</div>
                    <h1 style="margin:10px 0 10px 0;font-size:34px;line-height:1.1;color:#ffffff;">Kickbase Analyse {today}</h1>
                    <p style="margin:0;max-width:640px;font-size:15px;line-height:1.6;color:#d9e7f2;">Markt, Budgets und Kader in einer Uebersicht, damit du am Abend schneller entscheiden kannst, wen du halten, verkaufen oder kaufen willst.</p>
                </div>

                <div style="margin-top:20px;font-size:0;">
                    {summary_cards}
                </div>

                <div style="margin-top:8px;overflow-x:auto;">
                    {top_actions_section}
            {ai_section}
                    {market_section}
                    {squad_section}
                </div>

                <div style="padding:20px 8px 8px 8px;text-align:center;">
                    <p style="margin:0 0 10px 0;font-size:14px;color:#334e68;">Viel Erfolg beim Traden.<br><strong>Dein KickAdvisor Bot</strong></p>
                    <p style="margin:0;font-size:11px;color:#7b8794;">
                        Generiert mit dem <a href="https://github.com/LennardFe/Kickbase-Trading-Advisor" style="color:#486581;text-decoration:none;font-weight:700;">Kickbase Trading Advisor</a>
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """, subtype="html")

    # Versand
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
        
    print("\nEmail erfolgreich mit KI-Analyse versendet!")
