from flask import Flask, request, render_template, jsonify, send_from_directory
import os
from color_extractor import extract_and_sort_colors, rgb_to_hex
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'static/output'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 禁用文件缓存，提升安全性

# 确保上传和输出目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract_colors():
    if 'image' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            num_colors = int(request.form.get('num_colors', 5))
            colors = extract_and_sort_colors(
                file_path, 
                num_colors=num_colors,
                output_folder=app.config['OUTPUT_FOLDER']
            )
            
            # 构建响应数据
            result = {
                'colors': [rgb_to_hex(color) for color in colors],
                'files': {
                    'css': '/static/output/color_palette.css',
                    'html': '/static/output/color_palette.html',
                    'color_card': '/static/output/color_card.png',
                    'ui_preview': '/static/output/ui_preview.png'
                }
            }
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': f'处理图片时出错: {str(e)}'}), 500
        finally:
            # 清理上传的文件
            if os.path.exists(file_path):
                os.remove(file_path)
    
    return jsonify({'error': '不支持的文件类型'}), 400

if __name__ == '__main__':
    app.run(debug=True)
