import os
import io
import time
import shutil
import requests
import numpy as np
import pandas as pd
from io import BytesIO, StringIO
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

# --- DIRECTORY SETUP ---
TEMPLATE_DIR = "./generated_templates"
OUTPUT_DIR = "./BOD_POSTS"
SLIDES_DIR = "./BOD_SLIDES"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Clear old output files before generating fresh ones
for filename in os.listdir(OUTPUT_DIR):
    file_path = os.path.join(OUTPUT_DIR, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print(f"Failed to delete {file_path}. Reason: {e}")


# Helper for loading fonts safely on Ubuntu/GitHub Runners
def get_font(font_size):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, font_size)
            except Exception:
                pass
    return ImageFont.load_default()


# ==============================================================================
# 1. BAN FILE
# ==============================================================================
print("Processing BAN File...")
try:
    url = "https://nsearchives.nseindia.com/content/fo/fo_secban.csv"
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/",
        "Connection": "keep-alive"
    }
    session.get("https://www.nseindia.com", headers=headers, timeout=10)
    response = session.get(url, headers=headers, timeout=30)
    df = pd.read_csv(StringIO(response.text))
    if df.empty:
        raise ValueError("The DataFrame is empty. Skipping Ban file execution.")

    template_path = os.path.join(TEMPLATE_DIR, "BAN TEMPLATE.png")
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    rows = [f"{i+1}. {sec}" for i, sec in enumerate(df.iloc[:, 0])]
    textbox_left, textbox_top, textbox_right, textbox_bottom = 120, 360, 960, 1180
    textbox_height = textbox_bottom - textbox_top
    max_visible_rows = 6
    base_font_size, min_font_size = 70, 35

    if len(rows) > max_visible_rows:
        scale_factor = max_visible_rows / len(rows)
        row_font_size = max(int(base_font_size * scale_factor), min_font_size)
    else:
        row_font_size = base_font_size

    row_font = get_font(row_font_size)
    bbox = row_font.getbbox("Ag")
    text_height = bbox[3] - bbox[1]

    if len(rows) > 1:
        available_spacing = textbox_height - (len(rows) * text_height)
        line_spacing = max(10, min(available_spacing // (len(rows) - 1), 60))
    else:
        line_spacing = 0

    total_content_height = (len(rows) * text_height) + ((len(rows) - 1) * line_spacing)
    start_y = textbox_top + ((textbox_height - total_content_height) // 2)

    for i, row in enumerate(rows):
        y_position = start_y + i * (text_height + line_spacing)
        draw.text((textbox_left + 20, y_position), row, fill=(0, 0, 0), font=row_font)

    output_path = os.path.join(OUTPUT_DIR, "BAN FILE.png")
    img.save(output_path)
    print(f"Saved: {output_path}")
except Exception as e:
    print("Error in BAN FILE:", e)


# ==============================================================================
# 2. RESULTS FILE
# ==============================================================================
print("Processing RESULTS File...")
try:
    sheet_id = "15f-HEzUCwXiiBf29MvXaebFuCB-xX_JkjVBCAZjBXFE"
    gid = "0"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df = df[df['PURPOSE'].str.contains('Financial Results', na=False)]
    today_dt = pd.Timestamp('today').normalize()

    df['DATE'] = pd.to_datetime(df['DATE'])
    df = df.loc[df['DATE'] == today_dt, [df.columns[0]]]
    if df.empty:
        raise ValueError("No results scheduled for today. Skipping Results file execution.")

    df.drop_duplicates(inplace=True)
    template_path = os.path.join(TEMPLATE_DIR, "RESULTS TEMPLATE.png")
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    rows = [f"{i+1}. {sec}" for i, sec in enumerate(df.iloc[:, 0])]
    textbox_left, textbox_top, textbox_right, textbox_bottom = 120, 360, 960, 1180
    textbox_height = textbox_bottom - textbox_top
    max_visible_rows = 6
    base_font_size, min_font_size = 70, 35

    if len(rows) > max_visible_rows:
        scale_factor = max_visible_rows / len(rows)
        row_font_size = max(int(base_font_size * scale_factor), min_font_size)
    else:
        row_font_size = base_font_size

    row_font = get_font(row_font_size)
    bbox = row_font.getbbox("Ag")
    text_height = bbox[3] - bbox[1]

    if len(rows) > 1:
        available_spacing = textbox_height - (len(rows) * text_height)
        line_spacing = max(10, min(available_spacing // (len(rows) - 1), 60))
    else:
        line_spacing = 0

    total_content_height = (len(rows) * text_height) + ((len(rows) - 1) * line_spacing)
    start_y = textbox_top + ((textbox_height - total_content_height) // 2)

    for i, row in enumerate(rows):
        y_position = start_y + i * (text_height + line_spacing)
        draw.text((textbox_left + 20, y_position), row, fill=(0, 0, 0), font=row_font)

    output_path = os.path.join(OUTPUT_DIR, "RESULTS FILE.png")
    img.save(output_path)
    print(f"Saved: {output_path}")
except Exception as e:
    print("Error in RESULTS FILE:", e)


# ==============================================================================
# 3. GLOBAL MARKETS FILE
# ==============================================================================
print("Processing GLOBAL MARKETS File...")
try:
    sheet_id = "1Y8NVXhtDs14IWiX8NyfvRknPaGWGNffJ"
    gid = "1616651905"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()

    template_path = os.path.join(TEMPLATE_DIR, "GLOBAL TEMPLATE.png")
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    textbox_left, textbox_top, textbox_right = 120, 360, 960

    rows = []
    for _, r in df.iterrows():
        rows.append([
            str(r["SYMBOL"]),
            f"{int(round(r['LTP'])):,}",
            f"{int(round(r['CHANGE'])):,}",
            f"{r['% CHANGE']:.2f}"
        ])
    headers = ["SYMBOL", "LTP", "CHANGE", "% CHANGE"]

    header_font = get_font(40)
    row_font = get_font(38)

    all_data = [headers] + rows
    col_widths = []
    for col in range(len(headers)):
        max_width = max(draw.textlength(str(row[col]), font=row_font) for row in all_data)
        col_widths.append(max_width + 40)

    total_width = sum(col_widths)
    scale = (textbox_right - textbox_left) / total_width
    col_widths = [int(w * scale) for w in col_widths]

    col_x = [textbox_left]
    for w in col_widths[:-1]:
        col_x.append(col_x[-1] + w)

    start_y = textbox_top + 80
    row_height = 85
    line_color = (220, 220, 220)

    for i, h in enumerate(headers):
        draw.text((col_x[i], textbox_top), h, fill=(0, 0, 0), font=header_font)
    draw.line([(textbox_left, textbox_top + 60), (textbox_right, textbox_top + 60)], fill=line_color, width=2)

    for i, row in enumerate(rows):
        y = start_y + i * row_height
        pct = float(row[3])
        bg = (235, 255, 235) if pct > 0 else (255, 235, 235)
        text_color = (0, 120, 0) if pct > 0 else (160, 0, 0)

        draw.rectangle([(textbox_left, y - 10), (textbox_right, y + 60)], fill=bg)
        for j, cell in enumerate(row):
            text = str(cell)
            if j == 0:
                x = col_x[j] + 10
            else:
                text_w = draw.textlength(text, font=row_font)
                x = col_x[j] + col_widths[j] - text_w - 10
            color = text_color if j == 3 else (0, 0, 0)
            draw.text((x, y), text, fill=color, font=row_font)
        draw.line([(textbox_left, y + 60), (textbox_right, y + 60)], fill=line_color, width=1)

    output_path = os.path.join(OUTPUT_DIR, "GLOBAL FILE.png")
    img.save(output_path)
    print(f"Saved: {output_path}")
except Exception as e:
    print("Error in GLOBAL FILE:", e)


# ==============================================================================
# 4. INDIA VIX FILE
# ==============================================================================
print("Processing INDIA VIX File...")
try:
    sheet_id = "1Y8NVXhtDs14IWiX8NyfvRknPaGWGNffJ"
    gid = "278014969"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)

    nifty, vix, percent_move, support, resistance = df.iloc[0, 1], df.iloc[1, 1], df.iloc[2, 1], df.iloc[3, 1], df.iloc[4, 1]

    template_path = os.path.join(TEMPLATE_DIR, "INDIA VIX.png")
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    textbox_left, textbox_top, textbox_right, textbox_bottom = 120, 360, 960, 760
    textbox_width = textbox_right - textbox_left
    textbox_height = textbox_bottom - textbox_top

    parts = [
        ("Nifty 50 closed the previous session at ", (0, 0, 0), "normal"),
        (f"{nifty}", (0, 0, 0), "bold"),
        (", while India VIX settled at ", (0, 0, 0), "normal"),
        (f"{vix}", (0, 0, 0), "bold"),
        (". Based on the current volatility, the expected daily movement stands at ", (0, 0, 0), "normal"),
        (f"{percent_move}%", (0, 0, 0), "bold"),
        (". Key support is placed near ", (0, 0, 0), "normal"),
        (f"{support}", (0, 140, 0), "bold"),
        (", whereas immediate resistance is seen around ", (0, 0, 0), "normal"),
        (f"{resistance}", (200, 0, 0), "bold"),
        (".", (0, 0, 0), "normal"),
    ]

    font_size = 52
    while font_size > 20:
        normal_font = get_font(font_size)
        bold_font = get_font(font_size + 2)
        lines = []
        current_line = []
        current_width = 0

        for text, color, style in parts:
            font = bold_font if style == "bold" else normal_font
            words = text.split(" ")
            for word in words:
                word_text = word + " "
                word_width = draw.textlength(word_text, font=font)
                if current_width + word_width > textbox_width:
                    lines.append(current_line)
                    current_line = []
                    current_width = 0
                current_line.append((word_text, color, font))
                current_width += word_width
        if current_line:
            lines.append(current_line)

        line_height = int(font_size * 1.7)
        total_height = len(lines) * line_height
        if total_height <= textbox_height:
            break
        font_size -= 2

    start_y = textbox_top + (textbox_height - total_height) // 2
    y = start_y
    for line in lines:
        x = textbox_left
        for word, color, font in line:
            draw.text((x, y), word, fill=color, font=font)
            x += draw.textlength(word, font=font)
        y += line_height

    output_path = os.path.join(OUTPUT_DIR, "INDIA VIX.png")
    img.save(output_path)
    print(f"Saved: {output_path}")
except Exception as e:
    print("Error in INDIA VIX:", e)


# ==============================================================================
# 5. NIFTY OI & PCR DATA PROCESSING
# ==============================================================================
print("Processing OI and PCR Files...")
try:
    from tvDatafeed import TvDatafeed, Interval

    def safe_get_hist(tv, symbol, exchange, interval, n_bars=10, retries=5, sleep_sec=2):
        for attempt in range(retries):
            try:
                df = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=n_bars)
                if df is not None and not df.empty:
                    return df
            except Exception as e:
                print(f"Attempt {attempt+1} failed for {symbol}: {e}")
            time.sleep(sleep_sec)
        raise Exception(f"Failed to fetch data for {symbol} after {retries} retries")

    HOLIDAYS = {
        "15012026", "26012026", "03032026", "26032026", "31032026",
        "03042026", "14042026", "01052026", "28052026", "26062026",
        "14092026", "02102026", "20102026", "10112026", "24112026", "25122026"
    }

    def get_previous_trading_day(date):
        while True:
            d = date.strftime("%d%m%Y")
            if date.weekday() < 5 and d not in HOLIDAYS:
                return date
            date -= timedelta(days=1)

    def get_nse_fo_url():
        today_dt = datetime.today()
        target = today_dt - timedelta(days=3) if today_dt.weekday() == 0 else today_dt - timedelta(days=1)
        date_str = get_previous_trading_day(target).strftime("%Y%m%d")
        url = f"https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{date_str}_F_0000.csv.zip"
        return url, get_previous_trading_day(target)

    def is_monthly_expiry_week(trading_day):
        days_to_tuesday = (1 - trading_day.weekday()) % 7
        upcoming_tuesday = trading_day + timedelta(days=days_to_tuesday)
        return (upcoming_tuesday + timedelta(days=7)).month != upcoming_tuesday.month

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.nseindia.com/"
    })
    session.get("https://www.nseindia.com", timeout=10)

    url, trading_day = get_nse_fo_url()
    res = session.get(url, timeout=30)
    res.raise_for_status()

    df = pd.read_csv(BytesIO(res.content), compression="zip")
    df = df[df["TckrSymb"] == "NIFTY"]

    tv = TvDatafeed()
    nifty = safe_get_hist(tv, "NSE:NIFTY", "NSE", Interval.in_daily)
    niftyltp = nifty.iloc[-1]["close"]

    if is_monthly_expiry_week(trading_day=trading_day):
        niftyfut = safe_get_hist(tv, "NSE:NIFTY2!", "NSE", Interval.in_daily)
    else:
        niftyfut = safe_get_hist(tv, "NSE:NIFTY1!", "NSE", Interval.in_daily)

    niftyfutltp = niftyfut.iloc[-1]["close"]
    gift = safe_get_hist(tv, "NSEIX:NIFTY1!", "NSEIX", Interval.in_1_minute)
    giftltp = gift.iloc[-1]["close"]

    basis = niftyfutltp - niftyltp
    giftadj = giftltp - basis

    df['TradDt'] = pd.to_datetime(df['TradDt'])
    df['XpryDt'] = pd.to_datetime(df['XpryDt'])
    df['DTE'] = (df['XpryDt'] - df['TradDt']).dt.days
    df = df[df["DTE"] != 0]

    pcdf = df.copy()
    df = df[df['DTE'] == df['DTE'].min()]
    df = df[df["FinInstrmTp"] == "IDO"]
    df["MONEYNESS"] = df.apply(lambda row: "ITM" if ((row["OptnTp"] == "CE" and row["StrkPric"] < row["UndrlygPric"]) or (row["OptnTp"] == "PE" and row["StrkPric"] > row["UndrlygPric"])) else "OTM", axis=1)
    df = df[df["MONEYNESS"] == "OTM"].sort_values(by='StrkPric').reset_index(drop=True)

    pdf = df[(df['OptnTp'] == 'PE') & (df['StrkPric'] >= df['UndrlygPric'] * 0.95)].sort_values(by='OpnIntrst', ascending=False).head(5).sort_values(by='StrkPric').reset_index(drop=True)
    cdf = df[(df['OptnTp'] == 'CE') & (df['StrkPric'] <= df['UndrlygPric'] * 1.05)].sort_values(by='OpnIntrst', ascending=False).head(5).sort_values(by='StrkPric').reset_index(drop=True)

    odf = pd.concat([pdf[['TckrSymb', 'StrkPric', 'OpnIntrst', 'ChngInOpnIntrst']], cdf[['TckrSymb', 'StrkPric', 'OpnIntrst', 'ChngInOpnIntrst']]], axis=0, ignore_index=True)

    atmdf = pcdf[pcdf["FinInstrmTp"] == "IDF"]
    atmdf = atmdf[atmdf['DTE'] == atmdf['DTE'].min()]
    close = atmdf['ClsPric'].iloc[0]
    pclose = atmdf['PrvsClsgPric'].iloc[0]

    pcdf = pcdf[pcdf["FinInstrmTp"] == "IDO"]
    pcdf = pcdf[pcdf['DTE'] == pcdf['DTE'].min()][['TckrSymb', 'StrkPric', 'OptnTp', 'OpnIntrst', 'ChngInOpnIntrst']].reset_index(drop=True)
    pcdf['CLOSE'] = close
    pcdf['PCLOSE'] = pclose
    pcdf['POI'] = pcdf['OpnIntrst'] - pcdf['ChngInOpnIntrst']

    tdf = pcdf.copy()
    ydf = pcdf.copy()

    tdf["MONEYNESS"] = tdf.apply(lambda row: "ITM" if ((row["OptnTp"] == "CE" and row["StrkPric"] < row["CLOSE"]) or (row["OptnTp"] == "PE" and row["StrkPric"] > row["CLOSE"])) else "OTM", axis=1)
    tdf = tdf[tdf["MONEYNESS"] == "OTM"]

    ydf["MONEYNESS"] = ydf.apply(lambda row: "ITM" if ((row["OptnTp"] == "CE" and row["StrkPric"] < row["PCLOSE"]) or (row["OptnTp"] == "PE" and row["StrkPric"] > row["PCLOSE"])) else "OTM", axis=1)
    ydf = ydf[ydf["MONEYNESS"] == "OTM"]

    tcdf = tdf.groupby('OptnTp', as_index=False)['ChngInOpnIntrst'].sum()
    tdf = tdf.groupby('OptnTp', as_index=False)['OpnIntrst'].sum()
    ydf = ydf.groupby('OptnTp', as_index=False)['POI'].sum()

    # --- GENERATE OI CHART ---
    odf["StrkPric"] = odf["StrkPric"].astype(int)
    odf = odf.sort_values("StrkPric").reset_index(drop=True)

    template_path = os.path.join(TEMPLATE_DIR, "OI.png")
    img = Image.open(template_path).convert("RGBA")
    img_width, img_height = img.size
    dpi = 100

    fig = plt.figure(figsize=(img_width / dpi, img_height / dpi), dpi=dpi)
    bg_ax = fig.add_axes([0, 0, 1, 1])
    bg_ax.imshow(img)
    bg_ax.axis("off")

    textbox_left, textbox_top, textbox_right, textbox_bottom = 110, 470, 960, 1040
    left, bottom = textbox_left / img_width, 1 - (textbox_bottom / img_height)
    width, height = (textbox_right - textbox_left) / img_width, (textbox_bottom - textbox_top) / img_height

    ax = fig.add_axes([left, bottom, width, height])
    x = np.arange(len(odf))
    oi, change_oi = odf["OpnIntrst"], odf["ChngInOpnIntrst"]
    bar_width = 0.36

    all_vals = pd.concat([oi, change_oi])
    ymin, ymax = all_vals.min(), all_vals.max()
    padding = (ymax - ymin) * 0.15
    ax.set_ylim(ymin - padding, ymax + padding)

    mid = len(odf) // 2
    ax.axvspan(-0.5, mid - 0.5, color="#D5F5E3", alpha=0.40)
    ax.axvspan(mid - 0.5, len(odf) - 0.5, color="#FADBD8", alpha=0.40)

    bars1 = ax.bar(x - bar_width/2, oi, width=bar_width, color="#1565C0", label="Open Interest", zorder=3)
    bars2 = ax.bar(x + bar_width/2, change_oi, width=bar_width, color="#EF6C00", label="Change in OI", zorder=3)

    yrange = ymax - ymin
    for bar in bars1:
        h = bar.get_height()
        offset = yrange * 0.015
        ax.text(bar.get_x() + bar.get_width()/2, h + offset if h >= 0 else h - offset, f"{h/100000:.1f}L", ha='center', va='bottom' if h >= 0 else 'top', fontsize=8, rotation=90, fontweight='bold')
    for bar in bars2:
        h = bar.get_height()
        offset = yrange * 0.015
        ax.text(bar.get_x() + bar.get_width()/2, h + offset if h >= 0 else h - offset, f"{h/100000:.1f}L", ha='center', va='bottom' if h >= 0 else 'top', fontsize=8, rotation=90, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(odf["StrkPric"].astype(str), fontsize=11, fontweight="bold")
    strike_vals = odf["StrkPric"].values
    x_pos = np.interp(giftadj, strike_vals, np.arange(len(strike_vals)))
    ax.axvline(x=x_pos, color="black", linestyle="dotted", linewidth=2.5, zorder=4)

    ax.text(mid/2 - 0.5, ymax + padding*0.03, "OTM PUT SIDE", ha='center', fontsize=13, fontweight='bold', color='green')
    ax.text(mid + (len(odf)-mid)/2 - 0.5, ymax + padding*0.03, "OTM CALL SIDE", ha='center', fontsize=13, fontweight='bold', color='darkred')
    ax.legend(loc='upper left', bbox_to_anchor=(0.01, 1.01), fontsize=10, frameon=False, ncol=2)
    ax.text(1.04, 1.09, f"DOTTED LINE REPRESENT BASIS ADJUSTED GIFT NIFTY = {giftadj:.0f} while current GIFT NIFTY FUTURES is at {giftltp:.0f}", transform=ax.transAxes, ha='right', va='bottom', fontsize=10, fontweight='bold')

    ax.grid(axis='y', linestyle='--', alpha=0.25, zorder=0)
    ax.set_facecolor((1, 1, 1, 0))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='y', labelsize=10)

    output_path = os.path.join(OUTPUT_DIR, "OI.png")
    plt.savefig(output_path, dpi=dpi, bbox_inches=None, pad_inches=0)
    plt.close(fig)
    print(f"Saved: {output_path}")

    # --- GENERATE PCR CHART ---
    lot_size = 65
    todayce, todaype = tdf.iloc[0, 1] / lot_size, tdf.iloc[1, 1] / lot_size
    todaydce, todaydpe = tcdf.iloc[0, 1] / lot_size, tcdf.iloc[1, 1] / lot_size
    yesce, yespe = ydf.iloc[0, 1] / lot_size, ydf.iloc[0, 1] / lot_size

    template_path = os.path.join(TEMPLATE_DIR, "PCR.png")
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    textbox_left, textbox_right, textbox_top = 80, 1000, 380
    base_h = 930 - textbox_top
    textbox_bottom = textbox_top + int(base_h * 1.58)
    box_w, box_h = textbox_right - textbox_left, textbox_bottom - textbox_top

    unit = box_h / 7
    h1, h2 = int(unit * 3), int(unit * 1)
    h3 = box_h - h1 - h2
    y0 = textbox_top
    y1, y2 = y0 + h1, y0 + h1 + h2

    bg_panel, mid_panel, text_color = (20, 24, 32, 255), (28, 32, 42, 255), (235, 235, 235, 255)
    call_color, put_color = "#4C78A8", "#E45756"

    def make_pie(values, title):
        fig, ax = plt.subplots(figsize=(5, 4), facecolor="#141A22")
        ax.pie(values, labels=["OTM CALL OI", "OTM PUT OI"], autopct="%1.1f%%", startangle=90, colors=[call_color, put_color], textprops={'color': 'white', 'fontsize': 16})
        ax.set_title(title, fontsize=20, color="white")
        ax.axis("equal")
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=220, facecolor="#141A22")
        plt.close(fig)
        buf.seek(0)
        return Image.open(buf).convert("RGBA")

    draw.rectangle([textbox_left, y0, textbox_right, y1], fill=bg_panel)
    draw.rectangle([textbox_left, y1, textbox_right, y2], fill=mid_panel)
    draw.rectangle([textbox_left, y2, textbox_right, textbox_bottom], fill=bg_panel)

    top_pie = make_pie([todayce, todaype], "Trading Day OTM OI (CALL vs PUT)").resize((box_w, h1))
    img.paste(top_pie, (textbox_left, y0), top_pie)

    font_pcr = get_font(34)
    draw.text((textbox_left + 30, y1 + int(h2 * 0.20)), f"Δ CE OI = {todaydce:,.0f} Lots", fill=text_color, font=font_pcr)
    draw.text((textbox_left + 30, y1 + int(h2 * 0.20) + 50), f"Δ PE OI = {todaydpe:,.0f} Lots", fill=text_color, font=font_pcr)

    bottom_pie = make_pie([yesce, yespe], "T-1 DAY OTM OI (CALL vs PUT)").resize((box_w, h3))
    img.paste(bottom_pie, (textbox_left, y2), bottom_pie)

    output_path = os.path.join(OUTPUT_DIR, "PCR.png")
    img.save(output_path)
    print(f"Saved: {output_path}")
except Exception as e:
    print("Error in OI & PCR processing:", e)


# ==============================================================================
# 6. ASSEMBLE BOD_SLIDES FOLDER
# ==============================================================================
print("Assembling BOD_SLIDES folder...")
try:
    # 1. Reset SLIDES_DIR
    if os.path.exists(SLIDES_DIR):
        shutil.rmtree(SLIDES_DIR)
    os.makedirs(SLIDES_DIR, exist_ok=True)
    for filename in os.listdir(SLIDES_DIR):
        file_path = os.path.join(SLIDES_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

    slide_counter = 1

    # 2. Add BOD_TODAY.jpg from TEMPLATE_DIR
    today_file = os.path.join(TEMPLATE_DIR, "BOD_TODAY.jpg")
    if os.path.exists(today_file):
        dest_path = os.path.join(SLIDES_DIR, f"{slide_counter}.jpg")
        shutil.copy(today_file, dest_path)
        print(f"Added Slide {slide_counter}: BOD_TODAY.jpg")
        slide_counter += 1
    else:
        print(f"Warning: {today_file} not found. Skipping intro slide.")

    # 3. Add generated images from BOD_POSTS (sorted alphabetically)
    if os.path.exists(OUTPUT_DIR):
        posts = sorted(os.listdir(OUTPUT_DIR))
        for post in posts:
            src_path = os.path.join(OUTPUT_DIR, post)
            if os.path.isfile(src_path):
                ext = os.path.splitext(post)[1]
                dest_path = os.path.join(SLIDES_DIR, f"{slide_counter}{ext}")
                shutil.copy(src_path, dest_path)
                print(f"Added Slide {slide_counter}: {post}")
                slide_counter += 1

    # 4. Add BOD_END.jpg from root directory (./)
    end_file = "./BOD_END.jpg"
    if os.path.exists(end_file):
        dest_path = os.path.join(SLIDES_DIR, f"{slide_counter}.jpg")
        shutil.copy(end_file, dest_path)
        print(f"Added Slide {slide_counter}: BOD_END.jpg")
    else:
        print(f"Warning: {end_file} not found. Skipping ending slide.")

    print("BOD_SLIDES generation complete!")
except Exception as e:
    print("Error during BOD_SLIDES assembly:", e)

print("BOD Post Generation Complete!")
