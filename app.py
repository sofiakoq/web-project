from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont, ImageOps
import textwrap
import os
import math


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def calculate_font_size(text, max_width, max_height, is_vertical):
    for font_size in range(120, 20, -2):
        font = 'impact.ttf'
        chars = 15 if is_vertical else 20
        wrapped = textwrap.fill(text, width=chars).split('\n')
        max_line_width = max(font.getlength(line) for line in wrapped)
        total_height = len(wrapped) * font_size * 1.2
        if max_line_width <= max_width and total_height <= max_height:
            return font_size, wrapped
    return 20, textwrap.fill(text, width=15).split('\n')

def make_meme(input_path, top_text, bottom_text, output_path):
    img = ImageOps.exif_transpose(Image.open(input_path))
    width, height = img.size
    is_vertical = height > width
    
    max_font = int(height * 0.08) if is_vertical else int(width * 0.12)
    text_area = width * 0.9 if is_vertical else width * 0.8
    
    draw = ImageDraw.Draw(img)
    
    if top_text:
        font_size, lines = calculate_font_size(top_text, text_area, height * 0.3, is_vertical)
        font = 'impact.ttf'
        y = height * 0.05
        for line in lines:
            line_width = font.getlength(line)
            x = (width - line_width) / 2
            draw.text(
                (x, y), line,
                fill='white', font=font,
                stroke_width=max(2, font_size//15),
                stroke_fill='black'
            )
            y += font_size * 1.2
    
    if bottom_text:
        font_size, lines = calculate_font_size(bottom_text, text_area, height * 0.25, is_vertical)
        font = 'impact.ttf'
        total_height = len(lines) * font_size * 1.2
        y = height * 0.95 - total_height
        for line in lines:
            line_width = font.getlength(line)
            x = (width - line_width) / 2
            draw.text(
                (x, y), line,
                fill='white', font=font,
                stroke_width=max(2, font_size//15),
                stroke_fill='black'
            )
            y += font_size * 1.2

    img.save(output_path)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        image = request.files["image"]
        top_text = request.form.get("top_text", "").strip().upper()
        bottom_text = request.form.get("bottom_text", "").strip().upper()
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], "input.jpg")
        image.save(input_path)
        
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], "meme.jpg")
        make_meme(input_path, top_text, bottom_text, output_path)
        
        return render_template("result.html", meme=output_path)
    
    return render_template("index.html")

@app.route("/download")
def download():
    return send_file("static/uploads/meme.jpg", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
