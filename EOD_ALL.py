import os
import io
import math
import shutil
import requests
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

# --- DIRECTORY SETUP ---
TEMPLATE_DIR = "./generated_templates"
OUTPUT_DIR = "./EOD_POSTS"
SLIDES_DIR = "./EOD_SLIDES"

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

# Helper for loading fonts safely on Linux runners
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

# Helper for standard financial tables (Top 10, Sectoral, Major Indices)
def generate_index_table(df, template_name, output_name, symbol_col="SYMBOL"):
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    df.columns = df.columns.str.strip()
    
    textbox_left, textbox_top, textbox_right = 120, 360, 960
    rows = []
    for _, r in df.iterrows():
        rows.append([
            str(r[symbol_col]),
            f"{int(round(r['LTP'])):,}",
            f"{int(round(r['CHANGE'])):,}",
            f"{r['% CHANGE']:.2f}"
        ])
    headers = [symbol_col, "LTP", "CHANGE", "% CHANGE"]
    
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
        
    output_path = os.path.join(OUTPUT_DIR, output_name)
    img.save(output_path)
    print(f"Saved: {output_path}")

# ==============================================================================
# 1. TOP 10 MOVERS
# ==============================================================================
print("Processing TOP 10 MOVERS...")
try:
    sheet_id = "1Y8NVXhtDs14IWiX8NyfvRknPaGWGNffJ"
    gid = "1058329151"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(url).iloc[0:10, 0:4]
    generate_index_table(df, "TOP 10 TEMPLATE.png", "TOP 10 MOVERS.png", symbol_col="SYMBOL")
except Exception as e:
    print("Error in TOP 10 MOVERS:", e)

# ==============================================================================
# 2. SECTORAL INDICES
# ==============================================================================
print("Processing SECTORAL INDICES...")
try:
    sheet_id = "1Y8NVXhtDs14IWiX8NyfvRknPaGWGNffJ"
    gid = "1706532708"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(url).iloc[0:5, 0:4]
    generate_index_table(df, "SECTORAL INDICES.png", "SECTORAL INDICES.png", symbol_col="INDEX")
except Exception as e:
    print("Error in SECTORAL INDICES:", e)

# ==============================================================================
# 3. MAJOR INDICES
# ==============================================================================
print("Processing MAJOR INDICES...")
try:
    sheet_id = "1Y8NVXhtDs14IWiX8NyfvRknPaGWGNffJ"
    gid = "112818648"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(url).iloc[0:3, 0:4]
    generate_index_table(df, "MAJOR INDICES.png", "MAJOR INDICES.png", symbol_col="INDEX")
except Exception as e:
    print("Error in MAJOR INDICES:", e)

# ==============================================================================
# 4. 52 WEEK HIGH LOW
# ==============================================================================
print("Processing 52 WEEK HIGH LOW...")
try:
    MAX_ROWS_PER_POST = 15
    sheet_id = "1Y8NVXhtDs14IWiX8NyfvRknPaGWGNffJ"
    gid = "470493539"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    df = df[df['REMARKS'].notna() & (df['REMARKS'] != 'NR')].iloc[:, [0, 3, 4, 5]].reset_index(drop=True)
    
    if df.empty:
        raise ValueError("The DataFrame is empty. Skipping 52W High Low.")

    def create_post(df_chunk, post_no):
        template_path = os.path.join(TEMPLATE_DIR, "52WHL.png")
        img = Image.open(template_path).convert("RGBA")
        draw = ImageDraw.Draw(img)
        
        textbox_left, textbox_top, textbox_right, textbox_bottom = 120, 360, 960, 1300
        table_width, table_height = textbox_right - textbox_left, textbox_bottom - textbox_top
        headers = ["SYMBOL", "52W HIGH", "52W LOW", "REMARKS"]
        
        rows = []
        for _, r in df_chunk.iterrows():
            rows.append([str(r["SYMBOL"]), f"{r['52 Week High']:,}", f"{r['52 Week Low']:,}", str(r["REMARKS"])])
            
        num_rows = len(rows)
        usable_height = table_height - 140
        row_height = min(55, max(45, usable_height // max(num_rows, 1)))
        
        header_font_size = max(22, min(24, int(row_height * 0.50)))
        row_font_size = max(18, min(24, int(row_height * 0.42)))
        
        header_font = get_font(header_font_size)
        row_font = get_font(row_font_size)
        
        col_widths = [int(table_width * 0.22), int(table_width * 0.22), int(table_width * 0.22), int(table_width * 0.34)]
        col_x = [textbox_left]
        for w in col_widths[:-1]:
            col_x.append(col_x[-1] + w)
            
        line_color = (220, 220, 220)
        header_y = textbox_top
        
        for i, h in enumerate(headers):
            text_w = draw.textlength(h, font=header_font)
            x = col_x[i] + (col_widths[i] - text_w) / 2
            draw.text((x, header_y), h, fill=(0, 0, 0), font=header_font)
        draw.line([(textbox_left, header_y + row_height), (textbox_right, header_y + row_height)], fill=line_color, width=2)
        
        start_y = header_y + row_height + 20
        for i, row in enumerate(rows):
            y = start_y + i * row_height
            remarks = row[3].lower()
            bg = (235, 255, 235) if "high" in remarks else (255, 235, 235)
            remark_color = (0, 120, 0) if "high" in remarks else (160, 0, 0)
            
            draw.rectangle([(textbox_left, y - 5), (textbox_right, y + row_height - 10)], fill=bg)
            for j, cell in enumerate(row):
                text = str(cell)
                if j == 0:
                    x = col_x[j] + 10
                else:
                    text_w = draw.textlength(text, font=row_font)
                    x = col_x[j] + col_widths[j] - text_w - 10
                color = remark_color if j == 3 else (0, 0, 0)
                draw.text((x, y), text, fill=color, font=row_font)
            draw.line([(textbox_left, y + row_height - 10), (textbox_right, y + row_height - 10)], fill=line_color, width=1)
            
        output_path = os.path.join(OUTPUT_DIR, f"52 WEEK HIGH LOW_{post_no}.png")
        img.save(output_path)
        print(f"Saved: {output_path}")

    total_posts = math.ceil(len(df) / MAX_ROWS_PER_POST)
    for post_no in range(total_posts):
        start = post_no * MAX_ROWS_PER_POST
        end = start + MAX_ROWS_PER_POST
        df_chunk = df.iloc[start:end].reset_index(drop=True)
        create_post(df_chunk, post_no + 1)
except Exception as e:
    print("Error in 52 WEEK HIGH LOW:", e)

# ==============================================================================
# 5. ADVANCE DECLINE
# ==============================================================================
print("Processing ADVANCE DECLINE...")
try:
    sheet_id = "1Y8NVXhtDs14IWiX8NyfvRknPaGWGNffJ"
    gid = "734482448"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(url)
    
    advance = df.iloc[0, 1]
    decline = df.iloc[1, 1]
    total = advance + decline
    adv_pct = advance / total

    template_path = os.path.join(TEMPLATE_DIR, "ADR.png")
    img = Image.open(template_path).convert("RGBA")
    
    textbox_left, textbox_top, textbox_right, textbox_bottom = 120, 260, 960, 1300
    box_w, box_h = textbox_right - textbox_left, textbox_bottom - textbox_top
    
    gauge = Image.new("RGBA", (box_w, box_h + 120), (0, 0, 0, 0))
    draw = ImageDraw.Draw(gauge)
    
    track_color = (65, 65, 65)
    adv_color, dec_color = (0, 210, 120), (235, 70, 70)
    white, black, gray = (255, 255, 255), (15, 15, 15), (180, 180, 180)
    
    title_font = get_font(40)
    percent_font = get_font(40)
    label_font = get_font(42)
    number_font = get_font(64)
    tick_font = get_font(18)
    
    center_x, center_y = box_w // 2, 620
    radius, thickness = 310, 46
    bbox = [center_x - radius, center_y - radius, center_x + radius, center_y + radius]
    
    draw.arc(bbox, start=180, end=360, fill=track_color, width=thickness)
    adv_end = 180 + (180 * adv_pct)
    draw.arc(bbox, start=180, end=adv_end, fill=adv_color, width=thickness)
    draw.arc(bbox, start=adv_end, end=360, fill=dec_color, width=thickness)
    
    for i in range(11):
        angle_deg = 180 + (18 * i)
        angle_rad = np.radians(angle_deg)
        x1 = center_x + (radius + 16) * np.cos(angle_rad)
        y1 = center_y + (radius + 16) * np.sin(angle_rad)
        x2 = center_x + (radius - 24) * np.cos(angle_rad)
        y2 = center_y + (radius - 24) * np.sin(angle_rad)
        draw.line([(x1, y1), (x2, y2)], fill=(210, 210, 210), width=3)
        
        tx = center_x + (radius + 52) * np.cos(angle_rad)
        ty = center_y + (radius + 52) * np.sin(angle_rad)
        label = str(i * 10)
        tw = draw.textlength(label, font=tick_font)
        draw.text((tx - tw / 2, ty - 10), label, fill=gray, font=tick_font)
        
    title = "ADVANCE / DECLINE"
    tw = draw.textlength(title, font=title_font)
    draw.text(((box_w - tw) / 2, 60), title, fill=white, font=title_font)
    
    needle_angle = np.radians(180 + (180 * adv_pct))
    nx = center_x + (radius - 40) * np.cos(needle_angle)
    ny = center_y + (radius - 40) * np.sin(needle_angle)
    draw.line([(center_x, center_y), (nx, ny)], fill=black, width=8)
    draw.ellipse([center_x - 14, center_y - 14, center_x + 14, center_y + 14], fill=black)
    
    pct_text = f"{adv_pct * 100:.1f}% "
    tw = draw.textlength(pct_text, font=percent_font)
    draw.text(((box_w - tw) / 2, 760), pct_text, fill=adv_color if adv_pct >= 0.5 else dec_color, font=percent_font)
    
    half_w = box_w // 2
    adv_label, adv_num = "ADVANCE", str(advance)
    label_w = draw.textlength(adv_label, font=label_font)
    draw.text(((half_w // 2) - label_w / 2, 780), adv_label, fill=adv_color, font=label_font)
    num_w = draw.textlength(adv_num, font=number_font)
    draw.text(((half_w // 2) - num_w / 2, 825), adv_num, fill=(20, 20, 20), font=number_font)
    
    dec_label, dec_num = "DECLINE", str(decline)
    dec_center_x = half_w + (half_w // 2)
    dec_label_w = draw.textlength(dec_label, font=label_font)
    draw.text((dec_center_x - dec_label_w / 2, 780), dec_label, fill=dec_color, font=label_font)
    dec_num_w = draw.textlength(dec_num, font=number_font)
    draw.text((dec_center_x - dec_num_w / 2, 825), dec_num, fill=(20, 20, 20), font=number_font)
    
    img.paste(gauge, (textbox_left, textbox_top), gauge)
    
    output_path = os.path.join(OUTPUT_DIR, "ADVANCE_DECLINE.png")
    img.save(output_path)
    print(f"Saved: {output_path}")
except Exception as e:
    print("Error in ADVANCE DECLINE:", e)

# ==============================================================================
# 6. ASSEMBLE EOD_SLIDES FOLDER
# ==============================================================================
print("Assembling EOD_SLIDES folder...")
try:
    # 1. Clear or create EOD_SLIDES directory
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

    # 2. Copy EOD_TODAY.jpg from TEMPLATE_DIR as Slide 1
    today_file = os.path.join(TEMPLATE_DIR, "EOD_TODAY.jpg")
    if os.path.exists(today_file):
        dest_path = os.path.join(SLIDES_DIR, f"{slide_counter}.jpg")
        shutil.copy(today_file, dest_path)
        print(f"Added Slide {slide_counter}: EOD_TODAY.jpg")
        slide_counter += 1
    else:
        print(f"Warning: {today_file} not found. Skipping intro slide.")

    # 3. Copy generated images from EOD_POSTS sequentially
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

    # 4. Copy EOD_END.jpg from root directory (./) as the final slide
    end_file = "./EOD_END.jpg"
    if os.path.exists(end_file):
        dest_path = os.path.join(SLIDES_DIR, f"{slide_counter}.jpg")
        shutil.copy(end_file, dest_path)
        print(f"Added Slide {slide_counter}: EOD_END.jpg")
    else:
        print(f"Warning: {end_file} not found. Skipping ending slide.")

    print("EOD_SLIDES generation complete!")
except Exception as e:
    print("Error during EOD_SLIDES assembly:", e)

print("EOD Post Generation Complete!")
