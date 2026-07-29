import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# --- SETUP WORK DIRECTORIES ---
SOURCE_FOLDER = "."  # Source files lie in the main root directory
LOCAL_TEMPLATE_DIR = "./generated_templates"
os.makedirs(LOCAL_TEMPLATE_DIR, exist_ok=True)

today = pd.Timestamp.today().strftime('%d/%m/%y')

# --- FONT HELPER ---
def get_font(size):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except:
        return ImageFont.load_default()

# ==============================================================================
# 1. FRONT TEMPLATES (BOD_TEMP & EOD_TEMP)
# ==============================================================================
x = 320
y = 90
front_font = get_font(60)
files = ["BOD_TEMP.jpg", "EOD_TEMP.jpg"]

for filename in files:
    image_path = os.path.join(SOURCE_FOLDER, filename)
    
    if os.path.exists(image_path):
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        # Draw today's date in Navy Blue
        draw.text((x, y), today, fill=(15, 36, 85), font=front_font)
        
        output_name = filename.replace("_TEMP", "_TODAY")
        output_path = os.path.join(LOCAL_TEMPLATE_DIR, output_name)
        img.save(output_path)
        print(f"Generated: {output_path}")
    else:
        print(f"Skipped {filename}: File not found in main directory.")


# ==============================================================================
# 2. INSTAGRAM CANVA TEMPLATES
# ==============================================================================
def create_insta_template(text, output_filename, logo_path=None):
    width, height = 1080, 1440
    img = Image.new('RGBA', (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    navy_blue, black = (26, 54, 93), (0, 0, 0)
    inner_margin = 45

    draw.rectangle([20, 20, width - 20, height - 20], outline=navy_blue, width=1)
    draw.rectangle([inner_margin, inner_margin, width - inner_margin, height - inner_margin], outline=navy_blue, width=4)

    def draw_sparkle(draw_obj, center_x, center_y, size_px, color):
        points = [
            (center_x, center_y - size_px),
            (center_x + size_px/4, center_y - size_px/4),
            (center_x + size_px, center_y),
            (center_x + size_px/4, center_y + size_px/4),
            (center_x, center_y + size_px),
            (center_x - size_px/4, center_y + size_px/4),
            (center_x - size_px, center_y),
            (center_x - size_px/4, center_y - size_px/4)
        ]
        draw_obj.polygon(points, fill=color)

    draw_sparkle(draw, 930, 100, 25, navy_blue)
    draw_sparkle(draw, 960, 80, 12, navy_blue)
    draw_sparkle(draw, 120, height - 100, 25, navy_blue)
    draw_sparkle(draw, 90, height - 80, 12, navy_blue)

    left, right = inner_margin + 20, width - inner_margin - 20
    usable_width = right - left
    font_size = 85

    while font_size >= 30:
        font_header = get_font(font_size)
        bbox = draw.textbbox((0, 0), text, font=font_header)
        text_width = bbox[2] - bbox[0]
        if text_width <= usable_width:
            break
        font_size -= 2

    x_pos = left + (usable_width - text_width) / 2
    y_pos = 220
    draw.text((x_pos, y_pos), text, fill=black, font=font_header)

    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo_w = 180
        aspect_ratio = logo.size[1] / logo.size[0]
        logo_h = int(logo_w * aspect_ratio)
        logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        padding = 5
        logo_x = width - inner_margin - logo_w - padding
        logo_y = height - inner_margin - logo_h - padding
        img.paste(logo, (logo_x, logo_y), logo)

    output_path = os.path.join(LOCAL_TEMPLATE_DIR, output_filename)
    img.save(output_path)
    print(f"Generated: {output_path}")

# Logo file in main directory
my_logo_path = 'Logo_PNG.png'

templates_to_create = [
    (f"BAN {today}", "BAN TEMPLATE.png"),
    (f"RESULTS {today}", "RESULTS TEMPLATE.png"),
    ("GLOBAL MARKETS", "GLOBAL TEMPLATE.png"),
    (f"TOP 10 MARKET MOVERS ({today})", "TOP 10 TEMPLATE.png"),
    (f"SECTORAL INDICES ({today})", "SECTORAL INDICES.png"),
    (f"MAJOR INDICES ({today})", "MAJOR INDICES.png"),
    ("SUPPORT RESISTANCE (INDIA VIX BASED)", "INDIA VIX.png"),
    (f"52 WEEK HIGH LOW ({today})", "52WHL.png"),
    (f"ADVANCE DECLINE RATIO ({today})", "ADR.png"),
    ("NIFTY OPEN INTEREST TOP 5 STRIKES\nCALL AND PUT SIDE WITHIN 3% RANGE", "OI.png"),
    ("NIFTY OTM CALL PUT OPEN INTEREST\nT AND T-1 TRADING DAYS BIFURCATION", "PCR.png"),
    (f"DELIVERY HEAVY STOCKS ({today})", "DELIVERY.png")
]

for title_text, file_name in templates_to_create:
    create_insta_template(title_text, file_name, logo_path=my_logo_path)