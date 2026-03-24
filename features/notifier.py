from datetime import datetime, timedelta
from email.message import EmailMessage
from zoneinfo import ZoneInfo
import smtplib
import os

def send_mail(budget_df, market_df, squad_df, email, ai_advice=None):
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

    # Styling Funktion für die Tabellen
    def style_df(df):
        return df.to_html(index=False, border=0, classes="dataframe", escape=False).replace(
            "<table",
            '<table style="width:100%;border-collapse:collapse;font-size:13px;margin:20px 0;"'
        ).replace(
            "<th>",
            '<th style="background:#2c3e50;color:white;padding:8px;text-align:left;border-bottom:1px solid #ddd;">'
        ).replace(
            "<td>",
            '<td style="padding:8px;border-bottom:1px solid #eee;">'
        ).replace(
            '<tr style="text-align: right;">',
            '<tr style="background-color:#fefefe;">'
        )

    # Vorbereitung der KI-Sektion (Nur wenn ai_advice vorhanden ist)
    ai_section = ""
    if ai_advice:
        ai_section = f"""
        <div style="background-color: #e8f4f8; border-left: 5px solid #2980b9; padding: 20px; margin-bottom: 30px; border-radius: 5px;">
            <h3 style="color: #2980b9; margin-top: 0;">🤖 Dein KI-Berater empfiehlt:</h3>
            <p style="white-space: pre-wrap; font-size: 15px; color: #2c3e50; line-height: 1.6; font-style: italic;">
                {ai_advice}
            </p>
        </div>
        """

    # E-Mail Inhalt zusammenbauen
    msg.set_content("Ergebnisse sind nur in der HTML-Ansicht sichtbar.", subtype="plain")
    msg.add_alternative(f"""\
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; margin: 0; padding: 20px;">
        <div style="max-width: 1000px; margin: auto; background: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); overflow-x: auto;">
            
            <h2 style="color: #2c3e50; text-align: center; margin-top: 0;">Kickbase Report für {today}</h2>
            
            {ai_section}

            <h3 style="color: #2c3e50; margin-top: 30px;">Manager Budgets</h3>
            <p style="font-size: 14px; color: #333;">Geschätzte Budgets deiner Konkurrenten:</p>
            {style_df(budget_df)}

            <h3 style="color: #2c3e50; margin-top: 30px;">Transfermarkt Empfehlungen</h3>
            <p style="font-size: 14px; color: #333;">Diese Spieler auf dem Markt steigen voraussichtlich im Wert:</p>
            {style_df(market_df)}

            <h3 style="color: #2c3e50; margin-top: 30px;">Dein Kader</h3>
            <p style="font-size: 14px; color: #333;">Status und Prognose für deine aktuellen Spieler:</p>
            {style_df(squad_df)}

            <p style="margin-top: 30px; font-size: 14px;">Viel Erfolg beim Traden! <br><b>Dein KickAdvisor Bot</b></p>
            
            <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
            <p style="font-size: 11px; color: gray; text-align: center;">
                Generiert mit dem <a href="https://github.com/LennardFe/Kickbase-Trading-Advisor" style="color: #888; text-decoration: none; font-weight: bold;">Kickbase Trading Advisor</a>
            </p>
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
