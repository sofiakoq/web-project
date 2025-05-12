from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_font(font_size):
    """Надежная функция получения шрифта с несколькими fallback-вариантами"""
    font_paths = [
        'impact.ttf'
    ]
    
    for path in font_paths:
        try:
            return ImageFont.truetype(path, font_size)
        except:
            continue
    
    try:
        return ImageFont.truetype("arial.ttf", font_size)
    except:
        return ImageFont.load_default(size=font_size)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'image' not in request.files:
            return "No file uploaded", 400
            
        image = request.files["image"]
        
        if image.filename == '':
            return "No selected file", 400
            
        top_text = request.form.get("top_text", "").strip().upper()
        bottom_text = request.form.get("bottom_text", "").strip().upper()
        
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], "temp_image")
        image.save(temp_path)
        
        try:
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], "input.jpg")
            with Image.open(temp_path) as img:
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                img.save(input_path, 'JPEG', quality=95)

            output_path = os.path.join(app.config['UPLOAD_FOLDER'], "meme.jpg")
            make_meme(input_path, top_text, bottom_text, output_path)
            
            try:
                os.remove(temp_path)
            except:
                pass
                
            return render_template("result.html", meme=output_path)
            
        except Exception as e:
            try:
                os.remove(temp_path)
            except:
                pass
            return f"Error processing image: {str(e)}", 500
    
    return render_template("index.html")

def make_meme(input_path, top_text, bottom_text, output_path):
    with Image.open(input_path) as img:
        width, height = img.size
        draw = ImageDraw.Draw(img)
        
        def calculate_font_size(text, max_width, max_height):
            for font_size in range(120, 20, -2):
                font = get_font(font_size)
                if not hasattr(font, 'getlength'):  # Проверяем что это объект шрифта
                    font = ImageFont.load_default(size=font_size)
                
                wrapped = []
                for chars in range(10, 30):
                    wrapped = textwrap.fill(text, width=chars).split('\n')
                    try:
                        max_line_width = max(font.getlength(line) for line in wrapped)
                    except AttributeError:
                        # Для старых версий Pillow
                        max_line_width = max(draw.textlength(line, font=font) for line in wrapped)
                    
                    total_height = len(wrapped) * font_size * 1.2
                    
                    if max_line_width <= max_width and total_height <= max_height:
                        return font_size, wrapped
            return 20, textwrap.fill(text, width=15).split('\n')
        
        if top_text:
            max_height = height * 0.3
            font_size, lines = calculate_font_size(top_text, width * 0.9, max_height)
            font = get_font(font_size)
            
            y = height * 0.03
            for line in lines:
                try:
                    line_width = font.getlength(line)
                except AttributeError:
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
            font = get_font(font_size)
            
            total_text_height = len(lines) * font_size * 1.2
            y = height * (1 - 0.05) - total_text_height
            
            for line in lines:
                try:
                    line_width = font.getlength(line)
                except AttributeError:
                    line_width = draw.textlength(line, font=font)
                
                x = (width - line_width) / 2
                draw.text(
                    (x, y), line,
                    fill='white', font=font,
                    stroke_width=max(2, font_size//15),
                    stroke_fill='black'
                )
                y += font_size * 1.2

        img.save(output_path, 'JPEG', quality=95)

@app.route("/download")
def download():
    return send_file("static/uploads/meme.jpg", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
