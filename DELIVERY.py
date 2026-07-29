import os
import requests
import pandas as pd
from io import StringIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# --- DIRECTORY SETUP ---
TEMPLATE_DIR = "./generated_templates"
OUTPUT_DIR = "./DELIVERY"

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

# Helper to load fonts safely
def get_font(font_size, font_type="Bold"):
    font_paths = [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans-{font_type}.ttf",
        f"/usr/share/fonts/truetype/liberation/LiberationSans-{font_type}.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, font_size)
            except Exception:
                pass
    return ImageFont.load_default()

print("Processing DELIVERY HEAVY STOCKS...")
try:
    today_str = datetime.now().strftime("%d%m%Y")
    base_url = "https://nsearchives.nseindia.com/archives/equities/mto/MTO_"
    url = f"{base_url}{today_str}.DAT"

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
    response.raise_for_status()

    # Parse NSE .DAT file
    df = pd.read_csv(StringIO(response.text), skiprows=3, engine='python')

    # Fetch stock symbols from Google Sheets
    sheet_id = "1Y8NVXhtDs14IWiX8NyfvRknPaGWGNffJ"
    gid = "1058329151"
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    sdf = pd.read_csv(sheet_url)
    symbols = sdf.iloc[:, 10].tolist()

    # Filter and format
    df = df[df["Sr No"].isin(symbols)]
    df = df.iloc[:, [1, -1]]
    df.columns = ["SYMBOL", "Delivery %"]
    df = df.sort_values(by="Delivery %", ascending=False).reset_index(drop=True).head(10)

    # Load template image
    template_path = os.path.join(TEMPLATE_DIR, "DELIVERY.png")
    if not os.path.exists(template_path):
        template_path = os.path.join(TEMPLATE_DIR, "DELIVERY TEMPLATE.png")

    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    textbox_left, textbox_top, textbox_right = 120, 360, 960

    rows = []
    for _, r in df.iterrows():
        rows.append([
            str(r["SYMBOL"]),
            f"{float(r['Delivery %']):.2f}"
        ])
    headers_text = ["SYMBOL", "DELIVERY %"]

    header_font = get_font(40, "Bold")
    row_font = get_font(38, "Bold")

    all_data = [headers_text] + rows
    col_widths = []
    for col in range(len(headers_text)):
        max_width = max(draw.textlength(str(row[col]), font=row_font) for row in all_data)
        col_widths.append(max_width + 60)

    total_width = sum(col_widths)
    scale = (textbox_right - textbox_left) / total_width
    col_widths = [int(w * scale) for w in col_widths]

    col_x = [textbox_left]
    for w in col_widths[:-1]:
        col_x.append(col_x[-1] + w)

    start_y = textbox_top + 80
    row_height = 85
    line_color = (220, 220, 220)
    header_bg = (220, 230, 255)

    # Draw Header
    draw.rectangle([(textbox_left, textbox_top - 10), (textbox_right, textbox_top + 60)], fill=header_bg)
    for i, h in enumerate(headers_text):
        text = str(h)
        if i == 0:
            x = col_x[i] + 10  # Left align symbol
        else:
            text_w = draw.textlength(text, font=header_font)
            x = col_x[i] + col_widths[i] - text_w - 10  # Right align %
        draw.text((x, textbox_top), text, fill=(0, 0, 0), font=header_font)
    draw.line([(textbox_left, textbox_top + 60), (textbox_right, textbox_top + 60)], fill=line_color, width=2)

    # Draw Rows
    for i, row in enumerate(rows):
        y = start_y + i * row_height
        draw.rectangle([(textbox_left, y - 10), (textbox_right, y + 60)], fill=(245, 245, 245))
        for j, cell in enumerate(row):
            text = str(cell)
            if j == 0:
                x = col_x[j] + 10
            else:
                text_w = draw.textlength(text, font=row_font)
                x = col_x[j] + col_widths[j] - text_w - 10
            draw.text((x, y), text, fill=(0, 0, 0), font=row_font)
        draw.line([(textbox_left, y + 60), (textbox_right, y + 60)], fill=line_color, width=1)

    output_path = os.path.join(OUTPUT_DIR, "DELIVERY.png")
    img.save(output_path)
    print(f"Successfully generated: {output_path}")

except Exception as e:
    print("Error generating DELIVERY file:", e)
