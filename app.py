from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont, ExifTags
import textwrap
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

def correct_image_orientation(img):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        exif = img._getexif()
        if exif is not None:
            orientation_value = exif.get(orientation)
            if orientation_value is not None:
                if orientation_value == 3:
                    img = img.rotate(180, expand=True)
                elif orientation_value == 6:
                    img = img.rotate(270, expand=True)
                elif orientation_value == 8:
                    img = img.rotate(90, expand=True)
    except Exception as e:
        print(f"Error correcting image orientation: {e}")
    
    return img

def make_meme(input_path, top_text, bottom_text, output_path):
    img = Image.open(input_path)
    img = correct_image_orientation(img)
    width, height = img.size
    draw = ImageDraw.Draw(img)

    def calculate_font_size(text, max_width, max_height):
        for font_size in range(120, 20, -2):
            font = ImageFont.truetype('impact.ttf', font_size)
            wrapped = []
            
            for chars in range(10, 30):
                wrapped = textwrap.fill(text, width=chars).split('\n')
                max_line_width = max(draw.textlength(line, font=font) for line in wrapped)
                total_height = len(wrapped) * font_size * 1.2
                
                if max_line_width <= max_width and total_height <= max_height:
                    return font_size, wrapped
        return 20, textwrap.fill(text, width=15).split('\n')
    
    if top_text:
        max_height = height * 0.3
        font_size, lines = calculate_font_size(top_text, width * 0.9, max_height)
        
        y = height * 0.03
        for line in lines:
            font = ImageFont.truetype('impact.ttf', font_size)
            line_width = draw.textlength(line, font=font)
            x = (width - line_width) / 2
            draw.text(
                (x, y), line,
                fill='white', font=font,
                stroke_width=max(2, font_size//15),
                stroke_fill='black'
            )
            y += font_size * 1.2
    
    if bottom_text:
        max_height = height * 0.25
        font_size, lines = calculate_font_size(bottom_text, width * 0.9, max_height)

        total_text_height = len(lines) * font_size * 1.2
        y = height * (1 - 0.05) - total_text_height
        
        for line in lines:
            font = ImageFont.truetype('impact.ttf', font_size)
            line_width = draw.textlength(line, font=font)
            x = (width - line_width) / 2
            draw.text(
                (x, y), line,
                fill='white', font=font,
                stroke_width=max(2, font_size//15),
                stroke_fill='black'
            )
            y += font_size * 1.2

    img.save(output_path)

@app.route("/download")
def download():
    return send_file("static/uploads/meme.jpg", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
