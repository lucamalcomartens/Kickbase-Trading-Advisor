def send_mail(manager_budgets_df, market_recommendations_df, squad_recommendations_df, email, ai_advice=None):
    if not email:
        print("\nNo email provided, skipping email sending.")
        return

    EMAIL_ADDRESS = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

    # Datum festlegen
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    date_to_show = now + timedelta(days=1) if now.hour >= 22 else now
    today = date_to_show.strftime("%d-%m-%Y")

    # AI Advice Sektion vorbereiten (nur wenn vorhanden)
    ai_section = ""
    if ai_advice:
        ai_section = f"""
        <div style="background-color: #f0f7ff; border-left: 5px solid #2c3e50; padding: 15px; margin-bottom: 25px;">
            <h2 style="color: #2c3e50; margin-top: 0;">KI-Empfehlung</h2>
            <p style="white-space: pre-wrap; font-size: 14px; color: #333;">{ai_advice}</p>
        </div>
        <hr style="border:none; border-top: 1px solid #eee; margin: 20px 0;">
        """

    msg = EmailMessage()
    msg["Subject"] = f"Kickbase: {today}"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email

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
        )

    msg.set_content("Sorry, results only via html visible.", subtype="plain")
    msg.add_alternative(f"""\
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; margin: 0; padding: 20px;">
        <div style="max-width: 1000px; margin: auto; background: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); overflow-x: auto;">
        
        <h2 style="color: #2c3e50; text-align: center; margin-top: 0;">Kickbase Report for {today}</h2>
        
        {ai_section}

        <h3 style="color: #2c3e50; margin-top: 30px;">Manager Budgets</h3>
        {style_df(manager_budgets_df)}

        <h3 style="color: #2c3e50; margin-top: 30px;">Current Market Predictions</h3>
        {style_df(market_recommendations_df)}

        <h3 style="color: #2c3e50; margin-top: 30px;">Your Squad Predictions</h3>
        {style_df(squad_recommendations_df)}

        <p style="margin-top: 20px; font-size: 14px;">Best regards, <br><b>Your KickAdvisor Bot</b></p>
        </div>
    </body>
    </html>
    """, subtype="html")

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
        
    print("\nEmail sent successfully!")
