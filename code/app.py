# -*- coding: utf-8 -*-
# https://bootstrapdoc.com/docs/5.0/content/tables
from flask import Flask,  request, jsonify,url_for,send_file,send_from_directory,session,render_template_string
from flask import render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user,current_user
import os,json, base64, paramiko,random, string, io,time,threading,socket,sys
from datetime import datetime,timedelta
from captcha.image import ImageCaptcha
from werkzeug.utils import secure_filename
import threading
import tkinter as tk
from tkinter import messagebox
app = Flask(__name__)
app.secret_key = os.urandom(24) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024 
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
if sys.stdout.encoding != 'UTF-8':
    sys.stdout.reconfigure(encoding='utf-8')
folders = []
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_content_from_button_id(button_id):
    # Your getContentFromButtonId function
    # This is just a direct translation of your PHP function to Python
    switcher = {
        'btn_video': 'videorect',
        'btn_image': 'imagerect',
        'btn_text': 'textrect',
        'btn_time': 'timerect',
        'btn_weather_text': 'weather_text_rect',
        'btn_weather_temperature': 'weather_temperature_rect',
        'btn_weather_logo': 'weather_logo_rect',
        'btn_weather_title': 'weather_title_rect',
        'btn_logo': 'logorect',
        'btn_cast': 'broadcastrect',
        'btn_web': 'webrect'
    }
    return switcher.get(button_id, '')

def convert_chinese_to_english(chinese_name):
    # 可以根據需要的轉換邏輯進行更改
    translations = {
        '圖片': 'imagerect',
        '影片': 'videorect',
        '時間': 'timerect',
        '天氣標題': 'weather_title_rect',
        '天氣內容': 'weather_text_rect',
        '天氣溫度': 'weather_temperature_rect',
        '天氣圖標': 'weather_logo_rect',
        '跑馬燈': 'textrect',
        'Logo': 'logorect',
        '廣播': 'broadcastrect',
        '網頁': 'webrect'
    }
    return translations.get(chinese_name, 'default_content')

def generate_xml(program_name):
     # 從資料庫中查詢對應 program_name 的矩形資料
    rectangles = Rectangle.query.filter_by(program_name=program_name).all()

    # 設定 XML 檔案儲存的資料夾
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)  # 如果 uploads 資料夾不存在則創建

    program_dir = os.path.join(uploads_dir)
    
    # 創建 XML 字串
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += f'<config>\n<program name="{program_name}">\n'

    # 遍歷矩形資料來生成 XML
    for rect_data in rectangles:
        name = rect_data.name
        x = round(rect_data.x)  # 將數值轉換為整數
        y = round(rect_data.y)
        width = round(rect_data.width)
        height = round(rect_data.height)
        src = rect_data.src if rect_data.src else ""

        # 將中文 name 轉換為英文用於 content
        content = convert_chinese_to_english(name)

        # 將內容添加到 XML
        xml += f'<{content} name="{name}" x="{x}" y="{y}" width="{width}" height="{height}" src="{src}"></{content}>\n'

    # 關閉 XML 標籤
    xml += '</program>\n</config>'

    # 將 XML 存入檔案
    filename = os.path.join(program_dir, f"{program_name}.xml")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml)

    return jsonify({'message': 'Rectangles saved and XML file generated successfully!'})

@app.route('/load-xml/<program_name>')
def load_xml(program_name):
    # 構建 XML 文件路徑
    static_folder = app.root_path + '/uploads/'
    xml_file_path = os.path.join(static_folder, f"{program_name}.xml")
    print(xml_file_path)
    # 检查文件是否存在
    if os.path.exists(xml_file_path):
        # 返回 XML 文件到前端
        return send_file(xml_file_path, mimetype='application/xml')
    else:
        return 'XML file not found', 404
# 路由

def list_folders(folder_path):
    folders = [f.path for f in os.scandir(folder_path) if f.is_dir()]
    if not folders:
        return ''
    html = '<div class="subfolders">'
    for folder in folders:
        folder_name = os.path.basename(folder)
        html += f'<div class="folder" data-path="{folder}"><span class="toggle-icon">▶</span>{folder_name}</div>'
        html += list_folders(folder)
    html += '</div>'
    return html 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/captcha')
def captcha():
    image = ImageCaptcha()
    captcha_text = ''.join(random.choices(string.digits, k=6))
    data = image.generate(captcha_text)
    image_path = io.BytesIO(data.read())
    
    # Store the captcha text in the session
    session['captcha_text'] = captcha_text
    
    return send_file(image_path, mimetype='image/png')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']
        captcha = request.form['captcha']

        # Validate captcha
        if 'captcha_text' in session and session['captcha_text'] == captcha:
            # Example validation (replace with actual validation against database)
            user = User.query.filter_by(account=account, password=password).first()

            if user:
                login_user(user)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('user'))
            else:
                flash('Invalid account or password.', 'error')
        else:
            flash('Invalid captcha.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect('/')

@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/file', methods=['GET', 'POST'])
@login_required
def file():
    root_path = './uploads/'
    
    # 管理員可以查看所有使用者的資料夾
    if current_user.authority == 'admin':
        folders = [f.name for f in os.scandir(root_path) if f.is_dir()]  # 只提取資料夾名稱，不包括完整路徑
    else:
        # 一般用戶只能查看自己的資料夾
        user_folder = os.path.join(root_path, str(current_user.username))
        folders = [os.path.basename(user_folder)] if os.path.exists(user_folder) else []

    folder_html = ''
    if folders:
        for folder in folders:
            folder_html += f'<div class="folder" data-path="{folder}"><span class="toggle-icon">▶</span>{folder}</div>'
            full_folder_path = os.path.join(root_path, folder)
            folder_html += list_folders(full_folder_path)  # 列出子資料夾
    else:
        folder_html = '<p style="color: white;">目前沒有可見的資料夾。</p>'

    return render_template('file.html', folder_html=folder_html)


@app.route('/create_folder', methods=['POST'])
@login_required
def create_folder():
    new_folder_name = request.form['newFolderName']

    # 根據用戶權限創建資料夾
    if current_user.authority == 'admin':
        # 管理員可以在根目錄創建任意資料夾
        user_folder = os.path.join('./uploads', str(current_user.username))
        folder_path = os.path.join(user_folder, new_folder_name)
    else:
        # 一般用戶只能在自己的資料夾下創建子資料夾
        user_folder = os.path.join('./uploads', str(current_user.username))
        folder_path = os.path.join(user_folder, new_folder_name)

    # 創建資料夾
    os.makedirs(folder_path, exist_ok=True)

    return jsonify({'message': '資料夾創建成功', 'folder_name': new_folder_name})


@app.route('/create_subfolder', methods=['POST'])
@login_required
def create_subfolder():
    parent_folder_path = request.form['parentFolderPath']
    new_subfolder_name = request.form['newSubfolderName']
    
    # 確保用戶只能在自己的資料夾或有權限的資料夾中創建子資料夾
    if current_user.authority != 'admin' and not parent_folder_path.startswith(f'./uploads/{current_user.username}'):
        return jsonify({'error': '無權限在此資料夾創建子資料夾'}), 403
    
    subfolder_path = os.path.join(parent_folder_path, new_subfolder_name)
    os.makedirs(subfolder_path, exist_ok=True)
    
    return jsonify({'message': '子資料夾創建成功'})


@app.route('/delete_folder', methods=['POST'])
@login_required
def delete_folder():
    folder_path = request.form.get('folderPath')
    
    # 檢查用戶權限
    if current_user.authority != 'admin' and not folder_path.startswith(f'./uploads/{current_user.username}'):
        return jsonify({'error': '無權限刪除此資料夾'}), 403

    try:
        if os.path.exists(folder_path):
            os.rmdir(folder_path)  # 刪除資料夾
            return jsonify({'message': '資料夾刪除成功'})
        else:
            return jsonify({'error': '資料夾不存在'})
    except Exception as e:
        return jsonify({'error': str(e)})

images = []

import os
import base64
from flask import jsonify, request
from flask_login import login_required

@app.route('/load_images')
@login_required
def load_images():
    folder_path = request.args.get('folderPath', '')
    if folder_path:
        images = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4'))]

    response_data = []
    for image in images:
        image_path = os.path.join(folder_path, image)
        file_extension = image.split('.')[-1].lower()  # Get file extension
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        response_data.append({
            'file_id': image,
            'name': image,
            'time': os.path.getmtime(image_path),
            'image_data': image_data,
            'file_type': file_extension  # Include file type in response
        })
    return jsonify(response_data)


@app.route('/upload', methods=['POST'])
@login_required
def upload():
    folder_path = request.args.get('folderPath', '')
    uploaded_files = []

    if 'images[]' in request.files:
        files = request.files.getlist('images[]')
        for file in files:
            if file.filename != '':  # 確保檔案名稱不為空
                target_file_path = os.path.join(folder_path, file.filename)
                file.save(target_file_path)  # 儲存檔案到指定路徑
                uploaded_files.append(file.filename)

    if uploaded_files:
        return jsonify({'message': 'Files uploaded successfully: ' + ', '.join(uploaded_files)})
    else:
        return jsonify({'message': 'No files uploaded.'}), 400

@app.route('/delete_images', methods=['POST'])
@login_required
def delete_images():
    folder_path = request.args.get('folderPath', '')
    selected_images = request.json.get('selectedImages', [])
    deleted_images = []
    for image in selected_images:
        image_path = os.path.join(folder_path, image)
        if os.path.exists(image_path):
            os.remove(image_path)
            deleted_images.append(image)
    if deleted_images:
        return jsonify({'message': 'Images deleted successfully: ' + ', '.join(deleted_images)})
    else:
        return jsonify({'message': 'No images deleted.'}), 400

@app.route('/download_image')
@login_required
def download_image():
    filename = request.args.get('filename', '')
    folder_path = request.args.get('folderPath', '')  # 获取文件夹路径
    if filename and folder_path:
        full_path = os.path.join(folder_path, filename)
        if os.path.exists(full_path):
            return send_from_directory(folder_path, filename)
        else:
            return 'Image not found', 404
    else:
        return 'Bad request', 400

@app.route('/view')
@login_required
def view():
    if current_user.authority == 'admin':
        # 管理員可以查看所有任務
        data = Tasks.query.all()
        show_execute = True
        show_clear = True
    else:
        # 普通用戶只能查看自己的任務
        data = Tasks.query.filter_by(user_id=current_user.id).all()
        show_execute = False
        show_clear = False  
    
    return render_template('view.html', data=data, show_execute=show_execute, show_clear=show_clear)

class Tasks(db.Model):
    __tablename__ = 'tasks'
    task_id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), nullable=False)
    time = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 新增 user_id 外鍵
    user = db.relationship('User', backref='tasks', lazy=True)
    def to_dict(self):
        return{
            'task_id':self.task_id,
            'task_name':self.task_name,
            'time':self.format_time()
        }
    def format_time(self):
        return self.time.strftime('%Y-%m-%d %H:%M:%S') if self.time else None
class Views(db.Model):
    __tablename__ = 'views'
    view_id = db.Column(db.Integer, primary_key=True)
    view_name = db.Column(db.String(255), nullable=False)
    resolution = db.Column(db.Text(64), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'), nullable=False)
    tasks = db.relationship('Tasks', backref='views', lazy=True)
class Rectangle(db.Model):
    __tablename__ = 'rectangles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(10), nullable=False)    
    program_name = db.Column(db.String(100))
    src = db.Column(db.String(255),nullable=True)
    def __init__(self, name, x, y, width, height, color,program_name,src=src):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.program_name = program_name
        self.src = src
class Interact_task(db.Model):
    __tablename__ = 'interact_task'
    task_id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), nullable=False)
    time = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 新增 user_id 外鍵
    user = db.relationship('User', backref='interact_task', lazy=True)
    def to_dict(self):
        return {
            'task_id': self.task_id,
            'task_name': self.task_name,
            'time': self.format_time()
        }

    def format_time(self):
        return self.time.strftime('%Y-%m-%d %H:%M:%S') if self.time else None
class Interacts(db.Model):
    __tablename__ = 'interacts'
    interact_id = db.Column(db.Integer, primary_key=True)
    interact_name = db.Column(db.String(255), nullable=False)
    resolution = db.Column(db.Text(64), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('interact_task.task_id'), nullable=False)
    interacts = db.relationship('Interact_task', backref='interacts', lazy=True)
class Interrupt_task(db.Model):
    __tablename__ = 'interrupt_task'
    task_id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), nullable=False)
    time = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 新增 user_id 外鍵
    user = db.relationship('User', backref='interrupt_task', lazy=True)
    def to_dict(self):
        return {
            'task_id': self.task_id,
            'task_name': self.task_name,
            'time': self.format_time()
        }

    def format_time(self):
        return self.time.strftime('%Y-%m-%d %H:%M:%S') if self.time else None
class Interrupts(db.Model):
    __tablename__ = 'interrupts'
    interrupt_id = db.Column(db.Integer, primary_key=True)
    interrupt_name = db.Column(db.String(255), nullable=False)
    resolution = db.Column(db.Text(64), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('interrupt_task.task_id'), nullable=False)
    interrupts = db.relationship('Interrupt_task', backref='interrupts', lazy=True)
class Terms(db.Model):
    __tablename__ = 'terms'
    group_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 新增 user_id 外鍵
    user = db.relationship('User', backref='terms', lazy=True)
class Term_mange(db.Model):
    __tablename__ = 'term_mange'
    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.String(255), nullable=False)
    term_name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.Text(64), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('terms.group_id'), nullable=True)
    terms = db.relationship('Terms', backref='term_mange', lazy=True)
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    account = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    ip = db.Column(db.String(255))  # 這裡的欄位名稱應該與你的資料庫表結構中的欄位名稱一致
    authority = db.Column(db.String(255))
    email = db.Column(db.String(255))
    address = db.Column(db.String(255))

@app.route('/getData_task', methods=['GET'])
@login_required
def get_data_task():
    tasks = Tasks.query.all()
    task_list = [{'task_id': task.task_id, 'task_name': task.task_name} for task in tasks]  # 將資料轉換成字典列表
    return jsonify(task_list)  # 回傳 JSON 格式的任務資料

@app.route('/getTaskDetails/<int:task_id>', methods=['GET'])
def get_task_details(task_id):
    task = Tasks.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    response = jsonify(task.to_dict())
    response.headers['Content-Type'] = 'application/json; charset=utf-8'  # Ensure correct encoding
    return response

@app.route('/getData_interactTask', methods=['GET'])
@login_required
def getData_interactTask():
    interact_task = Interact_task.query.all()
    task_list = [{'task_id': task.task_id, 'task_name': task.task_name} for task in interact_task]
    return jsonify(task_list)

@app.route('/getInteractTaskDetails/<int:task_id>', methods=['GET'])
def get_interact_task_details(task_id):
    task = Interact_task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    response = jsonify(task.to_dict())
    response.headers['Content-Type'] = 'application/json; charset=utf-8'  # Ensure correct encoding
    return response

@app.route('/getData_interruptTask', methods=['GET'])
def getData_interruptTask():
    interrupt_task = Interrupt_task.query.all()
    task_list = [{'task_id': task.task_id, 'task_name': task.task_name} for task in interrupt_task]  # 將資料轉換成字典列表
    return jsonify(task_list)

@app.route('/getInterruptTaskDetails/<int:task_id>', methods=['GET'])
def get_interrupt_task_details(task_id):
    task = Interrupt_task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    response = jsonify(task.to_dict())
    response.headers['Content-Type'] = 'application/json; charset=utf-8'  # Ensure correct encoding
    return response

@app.route('/create_task', methods=['POST'])
def create_task():
    if request.method == 'POST':
        # 从表单中获取数据
        task_name = request.form['task_name']
        # 将数据添加到数据库
        new_item = Tasks(task_name=task_name, user_id=current_user.id)
        db.session.add(new_item)
        db.session.commit()
        # 重定向到首页或其他页面
    return redirect(url_for('view'))

@app.route('/delete_tasks', methods=['POST'])
def delete_tasks():
    if request.method == 'POST':
        task_ids = request.json
        for task_id in task_ids:
            task = Tasks.query.get(task_id)
            if task:
                db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Tasks deleted successfully'})

@app.route('/get_task_info', methods=['POST'])
def get_task_info():
    if request.method == 'POST':
        task_id = request.json['task_id']
        task = Tasks.query.get(task_id)
        if task:
            return jsonify({'task_name': task.task_name, 'time': task.time})
        else:
            return jsonify({'error': 'Task not found'}), 404

@app.route('/add_views', methods=['POST'])
def add_views():
    if request.method == 'POST':
        data = request.json
        view_name = data.get('view_name')
        resolution = data.get('resolution')
        task_id = data.get('task_id')
        new_view = Views(view_name=view_name, resolution=resolution, task_id=task_id)
        db.session.add(new_view)
        db.session.commit()
    return redirect(url_for('view'))

@app.route('/get_views', methods=['GET'])
def get_views():
    task_id = request.args.get('task_id')
    if not task_id:
        return redirect(url_for('view'))
    try:
        views = Views.query.filter_by(task_id=task_id).all()
    except Exception as e:
        return redirect(url_for('view'))
    
    # 将节目数据转换成 HTML 表格形式
    view_table = ""
    for view in views:
        view_table += "<tr>"
        view_table += f"<td style='width:900px;'><input type='checkbox' class='view-checkbox' name='view-checkbox' value='{view.view_id}' data-view-id='{view.view_id}' data-view-name='{view.view_name}' data-resolution='{view.resolution}'></td>"
        view_table += f"<td style='width:1050px;'>{view.view_name}</td>"
        view_table += f"<td style='width:700px;'>{view.resolution}</td>"
        view_table += "<td style='width:650px;'><a href='#' id='edit_canvas' onclick='updateProgramNameAndShowModal()'>佈局</a></td>"
        view_table += "<td style='width:450px;'><a href='#' id='edit_canvas' onclick='showDialog9()'>循環</a></td>"
        view_table += "<td style='width:300px;'><a href='#' id='content' onclick='toggleEditContent()'>内容</a></td>"
        view_table += "</tr>"
    return view_table
    

@app.route('/get_view_info', methods=['POST'])
def get_view_info():
    if request.method == 'POST':
        view_id = request.json['view_id']
        # 根据视图 ID 从数据库中获取视图信息
        try:
            view = Views.query.filter_by(view_id=view_id).first()
            if view:
                return jsonify({'view_name': view.view_name, 'resolution': view.resolution})
            else:
                return jsonify({'error': 'View not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/delete_views', methods=['POST'])
def delete_views():
    view_ids = request.json.get('view_ids')
    for view_id in view_ids:
        view = Views.query.get(view_id)
        if view:
             db.session.delete(view)
        # 所有视图都被删除后才提交事务
    db.session.commit()
    return redirect(url_for('view'))

rectId_to_name = {
    'imagerect': '圖片',
    'textrect': '文字',
    'videorect': '影片',
    'timerect': '時間',
    'weather_title_rect': '天氣標題',
    'weather_logo_rect': '天氣圖標',
    'weather_temperature_rect': '天氣溫度',
    'weather_text_rect': '天氣內容',
    'logorect': 'Logo',
    'broadcastrect':'廣播',
    'webrect': '網頁'
    # 可以繼續增加其他對應
}
@app.route('/upload-file', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'}), 400

        file = request.files['file']
        program_name = request.form.get('programName')
        rect_id = request.form.get('rectId1')

        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join('static',app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # 将矩形 ID 转换为中文名称
            rect_name = rectId_to_name.get(rect_id, 'default_content')
            
            # 根据矩形的中文名称和节目名称查找矩形
            rectangle = Rectangle.query.filter_by(program_name=program_name, name=rect_name).first()
            if not rectangle:
                return jsonify({'success': False, 'error': 'Rectangle not found'}), 404

            # 更新矩形的 src 路径为完整路径
            rectangle.src = file_path
            db.session.commit()

            # 生成 XML 文件
            generate_xml(program_name)

            return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/upload_horizontal', methods=['POST'])
def upload_horizontal():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'}), 400

        file = request.files['file']
        program_name = request.form.get('programName')
        rect_id = request.form.get('rectId2')

        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join('static',app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # 将矩形 ID 转换为中文名称
            rect_name = rectId_to_name.get(rect_id, 'default_content')
            
            # 根据矩形的中文名称和节目名称查找矩形
            rectangle = Rectangle.query.filter_by(program_name=program_name, name=rect_name).first()
            if not rectangle:
                return jsonify({'success': False, 'error': 'Rectangle not found'}), 404

            # 更新矩形的 src 路径为完整路径
            rectangle.src = file_path
            db.session.commit()

            # 生成 XML 文件
            generate_xml(program_name)

            return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/save_and_generate_xml', methods=['POST'])
def save_and_generate_xml():
    data = request.get_json()
    program_name = data.get('program_name')
    rectangles = data.get('rectangles', [])

    try:
        uploads_dir = 'uploads'
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)

        program_dir = os.path.join(uploads_dir)
        if not os.path.exists(program_dir):
            os.makedirs(program_dir)

        # 迭代每個矩形資料並保存或更新
        for rect_data in rectangles:
            name = rect_data['name']
            x = rect_data['x']
            y = rect_data['y']
            width = rect_data['width']
            height = rect_data['height']
            color = rect_data.get('color', 'default_color')
            button_id = rect_data['id']
            src = rect_data.get('src', '')  # 確認 src 正確傳遞
            
            print(f"素材路徑: {src}")  # 檢查素材路徑是否傳遞正確

            # 查詢資料庫是否有現存的矩形
            existing_rect = Rectangle.query.filter_by(
                name=name, x=x, y=y, width=width, height=height, program_name=program_name
            ).first()

            if existing_rect:
                # 更新現有的矩形
                existing_rect.color = color
                existing_rect.src = src  # 更新素材路徑
            else:
                # 新增矩形
                new_rect = Rectangle(
                    name=name,
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    color=color,
                    program_name=program_name,
                    src=src  # 設定素材路徑
                )
                db.session.add(new_rect)
        
        try:
            db.session.commit()
        except Exception as commit_error:
            db.session.rollback()
            print(f"提交錯誤: {commit_error}")
            return jsonify({'error': str(commit_error)}), 500

        # 生成 XML 文件
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += f'<config>\n<program name="{program_name}">\n'

        for rect_data in rectangles:
            name = rect_data['name']
            x = round(rect_data['x'])
            y = round(rect_data['y'])
            width = round(rect_data['width'])   
            height = round(rect_data['height'])
            button_id = rect_data['id']
            content = get_content_from_button_id(button_id)
            src = rect_data.get('src', '')  # 再次檢查 src 路徑

            if src:  # 如果有素材路徑，加入到 XML 中
                xml += f'<{content} name="{name}" x="{x}" y="{y}" width="{width}" height="{height}" src="{src}"></{content}>\n'
            else:
                xml += f'<{content} name="{name}" x="{x}" y="{y}" width="{width}" height="{height}"></{content}>\n'

        xml += '</program>\n</config>'

        # 保存 XML 文件
        filename = os.path.join(program_dir, f"{program_name}.xml")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(xml)

        return jsonify({'message': 'Rectangles saved and XML file generated successfully!'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save_and_generate_xml2', methods=['POST'])
def save_and_generate_xml2():
    data = request.get_json()
    program_name = data.get('program_name')
    rectangles = data.get('rectangles2', [])

    try:
        uploads_dir = 'uploads'
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)

        program_dir = os.path.join(uploads_dir)
        if not os.path.exists(program_dir):
            os.makedirs(program_dir)

        # 迭代每個矩形資料並保存或更新
        for rect_data in rectangles:
            name = rect_data['name']
            x = rect_data['x']
            y = rect_data['y']
            width = rect_data['width']
            height = rect_data['height']
            color = rect_data.get('color', 'default_color')
            button_id = rect_data['id']
            src = rect_data.get('src', '')  # 確認 src 正確傳遞
            
            print(f"素材路徑: {src}")  # 檢查素材路徑是否傳遞正確

            # 查詢資料庫是否有現存的矩形
            existing_rect = Rectangle.query.filter_by(
                name=name, x=x, y=y, width=width, height=height, program_name=program_name
            ).first()

            if existing_rect:
                # 更新現有的矩形
                existing_rect.color = color
                existing_rect.src = src  # 更新素材路徑
            else:
                # 新增矩形
                new_rect = Rectangle(
                    name=name,
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    color=color,
                    program_name=program_name,
                    src=src  # 設定素材路徑
                )
                db.session.add(new_rect)
        
        try:
            db.session.commit()
        except Exception as commit_error:
            db.session.rollback()
            print(f"提交錯誤: {commit_error}")
            return jsonify({'error': str(commit_error)}), 500

        # 生成 XML 文件
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += f'<config>\n<program name="{program_name}">\n'

        for rect_data in rectangles:
            name = rect_data['name']
            x = round(rect_data['x'])
            y = round(rect_data['y'])
            width = round(rect_data['width'])   
            height = round(rect_data['height'])
            button_id = rect_data['id']
            content = get_content_from_button_id(button_id)
            src = rect_data.get('src', '')  # 再次檢查 src 路徑

            if src:  # 如果有素材路徑，加入到 XML 中
                xml += f'<{content} name="{name}" x="{x}" y="{y}" width="{width}" height="{height}" src="{src}"></{content}>\n'
            else:
                xml += f'<{content} name="{name}" x="{x}" y="{y}" width="{width}" height="{height}"></{content}>\n'

        xml += '</program>\n</config>'

        # 保存 XML 文件
        filename = os.path.join(program_dir, f"{program_name}.xml")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(xml)

        return jsonify({'message': 'Rectangles saved and XML file generated successfully!'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
@app.route('/rectangles/<program_name>', methods=['GET'])
def get_rectangles(program_name):
    try:
        rectangles = Rectangle.query.filter_by(program_name=program_name).all()
        if not rectangles:
            return jsonify({'error': 'No rectangles found for program name'}), 404
        # Prepare JSON response
        rectangles_data = []
        for rect in rectangles:
            rect_data = {
                'name': rect.name,
                'x': rect.x,
                'y': rect.y,
                'width': rect.width,
                'height': rect.height,
                'color': rect.color,
                'id': rect.id
            }
            rectangles_data.append(rect_data)
        return jsonify(rectangles_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_rectangle', methods=['POST'])
def update_rectangle():
    data = request.get_json()
    program_name = data.get('program_name')
    rectangle_name = data.get('rectangle_name')
    width = data.get('width')
    height = data.get('height')
    x = data.get('x')
    y = data.get('y')

    # 更新資料庫中的矩形資訊
    success = update_rectangle_in_db(program_name, rectangle_name, width, height, x, y)

    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Update failed'}), 400

# 更新矩形資訊的資料庫函數
def update_rectangle_in_db(program_name, rectangle_name, width, height, x, y):
    try:
        # 實作資料庫更新邏輯
        # 假設使用 SQLAlchemy 進行資料庫操作
        rectangle = Rectangle.query.filter_by(program_name=program_name, name=rectangle_name).first()
        if rectangle:
            rectangle.width = width
            rectangle.height = height
            rectangle.x = x
            rectangle.y = y
            db.session.commit()  # 提交更新
            generate_xml(program_name)
            return True
        return False  # 找不到對應的矩形
    except Exception as e:
        print(f"Error updating rectangle: {e}")
        return False

@app.route('/delete_rectangle', methods=['POST'])
def delete_rectangle():
    data = request.get_json()
    program_name = data.get('program_name')
    rectangle_name = data.get('rectangle_name')

    # 驗證後端是否接收到正確的資料
    print(f"Program Name: {program_name}, Rectangle Name: {rectangle_name}")

    # 查找資料庫中的對應矩形
    rectangle = Rectangle.query.filter_by(name=rectangle_name, program_name=program_name).first()

    if rectangle:
        # 刪除矩形
        db.session.delete(rectangle)
        db.session.commit()
        generate_xml(program_name)
        return jsonify({"success": True})
    else:
        # 打印錯誤信息
        print(f"Failed to find rectangle with name '{rectangle_name}' in program '{program_name}'")
        return jsonify({"success": False, "message": "Rectangle not found"})


@app.route('/interact')
@login_required
def interact():
    if current_user.authority == 'admin':
        # 管理員可以查看所有任務
        data = Interact_task.query.all()
        show_execute = True
        show_clear = True  
    else:
        # 普通用戶只能查看自己的任務
        data = Interact_task.query.filter_by(user_id=current_user.id).all()
        show_execute = False
        show_clear = False  
    
    return render_template('interact.html', data=data, show_execute=show_execute, show_clear=show_clear)

@app.route('/create_interactTask', methods=['POST'])
def create_interactTask():
    if request.method == 'POST':
        # 从表单中获取数据
        task_name = request.form['task_name']
        # 将数据添加到数据库
        new_item = Interact_task(task_name=task_name, user_id=current_user.id)
        db.session.add(new_item)
        db.session.commit()
        # 重定向到首页或其他页面
    return redirect(url_for('interact'))

@app.route('/delete_interactTask', methods=['POST'])
def delete_interactTask():
    if request.method == 'POST':
        task_ids = request.json
        for task_id in task_ids:
            task = Interact_task.query.get(task_id)
            if task:
                db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'interact_task deleted successfully'})

@app.route('/get_interactTask_info', methods=['POST'])
def get_interactTask_info():
    if request.method == 'POST':
        task_id = request.json['task_id']
        task = Interact_task.query.get(task_id)
        if task:
            return jsonify({'task_name': task.task_name, 'time': task.time})
        else:
            return jsonify({'error': 'Task not found'}), 404

@app.route('/add_interacts', methods=['POST'])
def add_interacts():
    if request.method == 'POST':
        data = request.json
        interact_name = data.get('interact_name')
        resolution = data.get('resolution')
        task_id = data.get('task_id')
        new_interact = Interacts(interact_name=interact_name, resolution=resolution, task_id=task_id)
        db.session.add(new_interact)
        db.session.commit()
    return redirect(url_for('interact'))

@app.route('/get_interacts', methods=['GET'])
def get_interacts():
    task_id = request.args.get('task_id')
    try:
        interacts = Interacts.query.filter_by(task_id=task_id).all()
    except Exception as e:
        return redirect(url_for('interact'))

    # 将节目数据转换成 HTML 表格形式
    interact_table = ""
    for interact in interacts:
        interact_table += "<tr>"
        interact_table += f"<td style='width:900px;'><input type='checkbox' class='interact-checkbox' name='interact-checkbox' value='{interact.interact_id}' data-interact-id='{interact.interact_id}' data-interact-name='{interact.interact_name}' data-resolution='{interact.resolution}'></td>"
        interact_table += f"<td style='width:1050px;'>{interact.interact_name}</td>"
        interact_table += f"<td style='width:700px;'>{interact.resolution}</td>"
        interact_table += "<td style='width:650px;'><a href='#' id='edit_canvas' onclick='updateProgramNameAndShowModal()'>佈局</a></td>"
        interact_table += "<td style='width:300px;'><a href='#' id='content' onclick='toggleEditContent()'>内容</a></td>"
        interact_table += "</tr>"  # 确保在每次迭代中都正确地关闭</tr>标签
    
    return interact_table

@app.route('/get_interact_info', methods=['POST'])
def get_interact_info():
    if request.method == 'POST':
        interact_id = request.json['interact_id']
        try:
            interact = Interacts.query.filter_by(interact_id=interact_id).first()
            if interact:
                return jsonify({'interact_name': interact.interact_name, 'resolution': interact.resolution})
            else:
                return jsonify({'error': 'Interact not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/delete_interacts', methods=['POST'])
def delete_interacts():
    interact_ids = request.json.get('interact_ids')
    for interact_id in interact_ids:
        interact = Interacts.query.get(interact_id)
        if interact:
             db.session.delete(interact)
        # 所有视图都被删除后才提交事务
    db.session.commit()
    return redirect(url_for('interact'))

@app.route('/interrupt')
@login_required
def interrupt():
    if current_user.authority == 'admin':
        # 管理員可以查看所有任務
        data = Interrupt_task.query.all()  
        show_execute = True
        show_clear = True
    else:
        # 普通用戶只能查看自己的任務
        data = Interrupt_task.query.filter_by(user_id=current_user.id).all()  
        show_execute = False
        show_clear = False
    
    return render_template('interrupt.html', data=data, show_execute=show_execute, show_clear=show_clear)

@app.route('/create_interruptTask', methods=['POST'])
def create_interruptTask():
    if request.method == 'POST':
        # 从表单中获取数据
        task_name = request.form['task_name']
        # 将数据添加到数据库
        new_item = Interrupt_task(task_name=task_name, user_id=current_user.id)
        db.session.add(new_item)
        db.session.commit()
        # 重定向到首页或其他页面
    return redirect(url_for('interrupt'))

@app.route('/delete_interruptTask', methods=['POST'])
def delete_interruptTask():
    if request.method == 'POST':
        task_ids = request.json
        for task_id in task_ids:
            task = Interrupt_task.query.get(task_id)
            if task:
                db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'interact_task deleted successfully'})

@app.route('/get_interruptTask_info', methods=['POST'])
def get_interruptTask_info():
    if request.method == 'POST':
        task_id = request.json['task_id']
        task = Interrupt_task.query.get(task_id)
        if task:
            return jsonify({'task_name': task.task_name, 'time': task.time})
        else:
            return jsonify({'error': 'interrupt_task not found'}), 404

@app.route('/add_interrupts', methods=['POST'])
def add_interrupts():
    if request.method == 'POST':
        data = request.json
        interrupt_name = data.get('interrupt_name')
        resolution = data.get('resolution')
        task_id = data.get('task_id')
        new_view = Interrupts(interrupt_name=interrupt_name, resolution=resolution, task_id=task_id)
        db.session.add(new_view)
        db.session.commit()
    return redirect(url_for('interrupt'))

@app.route('/get_interrupts', methods=['GET'])
def get_interrupts():
    task_id = request.args.get('task_id')   
    try:
        interrupts = Interrupts.query.filter_by(task_id=task_id).all()
    except Exception as e:
        return redirect(url_for('interrupt'))
    
    # 将节目数据转换成 HTML 表格形式
    interrupt_table = ""
    for interrupt in interrupts:
        interrupt_table += "<tr>"
        interrupt_table += f"<td style='width:900px;'><input type='checkbox' class='interrupt-checkbox' name='interrupt-checkbox' value='{interrupt.interrupt_id}' data-interrupt-id='{interrupt.interrupt_id}' data-interrupt-name='{interrupt.interrupt_name}' data-resolution='{interrupt.resolution}'></td>"
        interrupt_table += f"<td style='width:1050px;'>{interrupt.interrupt_name}</td>"
        interrupt_table += f"<td style='width:700px;'>{interrupt.resolution}</td>"
        interrupt_table += "<td style='width:650px;'><a href='#' id='edit_canvas' onclick='updateProgramNameAndShowModal()'>佈局</a></td>"
        interrupt_table += "<td style='width:300px;'><a href='#' id='content'  onclick='toggleEditContent()'>内容</a></td>"
        interrupt_table += "</tr>"  # 确保在每次迭代中都正确地关闭</tr>标签
    return interrupt_table

@app.route('/get_interrupt_info', methods=['POST'])
def get_interrupt_info():
    if request.method == 'POST':
        interrupt_id = request.json['interrupt_id']
        try:
            interrupt = Interrupts.query.filter_by(interrupt_id=interrupt_id).first()
            if interrupt:
                return jsonify({
                    'interrupt_name': interrupt.interrupt_name,
                    'resolution': interrupt.resolution
                })
            else:
                return jsonify({'error': 'Interrupt not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/delete_interrupts', methods=['POST'])
def delete_interrupts():
    interrupt_ids = request.json.get('interrupt_ids')
    for interrupt_id in interrupt_ids:
        interrupt = Interrupts.query.get(interrupt_id)
        if interrupt:
             db.session.delete(interrupt)
        # 所有视图都被删除后才提交事务
    db.session.commit()
    return redirect(url_for('interrupt'))

def send_files_to_rpi(hostname, port, username, password, local_files, remote_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)

    scp = ssh.open_sftp()
    for local_file in local_files:
        remote_file = os.path.join(remote_path, os.path.basename(local_file))
        scp.put(local_file, remote_file)
    scp.close()
    ssh.close()

@app.route('/terminal')
@login_required
def terminal():
    if current_user.authority == 'admin':
        # Admin can see all terminal commands and logs
        data = Terms.query.all()  # Fetch all terms
        show_execute = True
        show_clear = True
    elif current_user.authority == 'root':
        # Root user can execute commands and see their own logs
        data = Terms.query.filter_by(user_id=current_user.id).all()  # Filter by user ID
        show_execute = False
        show_clear = False
    else:
        # Regular users can only see their own logs and cannot execute commands
        data = Terms.query.filter_by(user_id=current_user.id).all()
        show_execute = False
        show_clear = False

    return render_template('terminal.html', data=data, show_execute=show_execute, show_clear=show_clear)

last_connected_time = {}
raspberry_ips = {}
# 伺服器IP和端口
server_ip = '0.0.0.0'  # 监听所有IP地址
server_port = 5002

def handle_raspberry_connections():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)
    print(f"伺服器已啟動，正在監聽 {server_ip}:{server_port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"收到來自 {addr} 的連接")

        try:
            # 接收樹莓派 ID 和 IP
            data = client_socket.recv(1024)
            if not data:
                print("接收到空數據")
                continue

            message = data.decode('utf-8')
            print(f"原始數據: {message}")

            # 確保數據格式正確
            if ',' not in message:
                print(f"數據格式錯誤: {message}")
                continue

            raspberry_id, raspberry_ip = message.split(',', 1)
            print(f"收到樹莓派 ID: {raspberry_id} 和 IP: {raspberry_ip}")

            # 更新樹莓派的最後連接時間和IP
            last_connected_time[raspberry_id] = datetime.now()
            raspberry_ips[raspberry_id] = raspberry_ip

        except (socket.error, UnicodeDecodeError) as e:
            print(f"錯誤: {e}")

        finally:
            client_socket.close()

# 啟動樹莓派連接處理的線程
threading.Thread(target=handle_raspberry_connections, daemon=True).start()

@app.route('/status', methods=['GET'])
def connection_status():
    group_id = request.args.get('group_id')
    
    if group_id:
        terms = Term_mange.query.filter_by(group_id=group_id).all()
    else:
        terms = Term_mange.query.all()

    now = datetime.now()
    statuses = []

    for term in terms:
        term_id = term.term_id
        term_name = term.term_name
        city = term.city

        last_time = last_connected_time.get(term_id)
        raspberry_ip = raspberry_ips.get(term_id)
        if last_time:
            time_since_last_connection = now - last_time
            time_since_last_connection_str = str(time_since_last_connection).split('.')[0]

            if time_since_last_connection > timedelta(seconds=15):
                status = "Offline"
            else:
                status = "Connected"
        else:
            status = "Offline"
            time_since_last_connection_str = 'N/A'
            last_time = 'N/A'
            raspberry_ip = 'N/A'

        statuses.append({
            "device_id": term_id,
            "device_name": term_name,
            "status": status,
            "last_connected_time": last_time if isinstance(last_time, str) else last_time.strftime('%Y-%m-%d %H:%M'),
            "time_since_last_connection": time_since_last_connection_str,
            "raspberry_ip": raspberry_ip,
            "city": city,
        })

    return jsonify(statuses), 200
def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'py', 'mkv','xml'}  # 允許的檔案格式
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def send_files_to_rpi(hostname, port, username, password, local_files, remote_path):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port, username, password)  # 設定超時時間為 60 秒

        scp = ssh.open_sftp()
        for local_file in local_files:
            remote_file = os.path.join(remote_path, os.path.basename(local_file))
            print(f"Sending file: {local_file} to {remote_file}")
            scp.put(local_file, remote_file, confirm=True)  # 確認傳輸完成
        scp.close()
        ssh.close()
    except Exception as e:
        print(f"Error sending files: {e}")
        raise Exception(f"Error sending files: {e}")



@app.route('/send_message/<device_id>', methods=['POST'])
def send_message(device_id):
    if device_id not in raspberry_ips:
        return jsonify({"error": "Invalid device ID"}), 404

    hostname = raspberry_ips[device_id]
    port = 22  # 默认 SSH 端口
    username = 'user'
    password = 'raspberry'
    remote_path = '/home/user/message.txt'  # 消息存储的远程文件路径

    # 从请求的 JSON 数据中获取消息
    data = request.get_json()
    message = data.get('message')

    if not message:
        return jsonify({"error": "No message provided"}), 400

    # 使用 SSH 发送消息到 Raspberry Pi
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname, port=port, username=username, password=password)
        # 将消息写入远程文件
        ssh.exec_command(f'echo "{message}" > {remote_path}')
        ssh.close()
        return jsonify({"message": "Message sent successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to send message: {str(e)}"}), 500

@app.route('/send_files/<device_id>', methods=['POST'])
def send_files(device_id):
    if device_id not in raspberry_ips:
        return jsonify({"error": "Invalid device ID"}), 404

    hostname = raspberry_ips[device_id]
    port = 22  # Default SSH port
    username = 'user'
    password = 'raspberry'
    remote_path = '/home/user/'

    all_files = []
    if 'files' in request.files:
        files = request.files.getlist('files')
        for file in files:
            if file and allowed_file(file.filename):  # 檢查檔案格式
                filename = secure_filename(file.filename)  # 確保檔名安全
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                all_files.append(filepath)
            else:
                return jsonify({"error": f"File type not allowed: {file.filename}"}), 400

    if not all_files:
        return jsonify({"error": "No valid files selected"}), 400

    try:
        send_files_to_rpi(hostname, port, username, password, all_files, remote_path)
    except Exception as e:
        return jsonify({"error": f"Failed to send files: {str(e)}"}), 500

    for file in all_files:
        os.remove(file)

    return jsonify({"message": "Files sent successfully!"})

def execute_remote_command(hostname, port, username, password, command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port=port, username=username, password=password)
        full_command = f'export DISPLAY=:0 && {command}'  # 设置 DISPLAY 变量
        stdin, stdout, stderr = ssh.exec_command(full_command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()
        return {'output': output, 'error': error}
    except Exception as e:
        return {'error': str(e)}

# 使用 device_id 来查找树莓派并执行命令
@app.route('/execute/<device_id>', methods=['POST'])
def execute(device_id):
    if device_id not in raspberry_ips:
        return jsonify({"error": "Invalid device ID"}), 404

    hostname = raspberry_ips[device_id]
    port = 22  # 默认的 SSH 端口
    username = 'user'
    password = 'raspberry'

    data = request.get_json()
    command = data.get('command')

    if not command:
        return jsonify({"error": "No command provided"}), 400

    # 执行远程命令
    result = execute_remote_command(hostname, port, username, password, command)
    return jsonify(result)

@app.route('/create_group', methods=['POST'])
@login_required  # 確保用戶已登錄
def create_group():
    if request.method == 'POST':
        # 從表單中獲取數據
        group_name = request.form['group_name']
        
        # 獲取當前用戶的 user_id
        user_id = current_user.id
        
        # 將數據添加到數據庫
        new_item = Terms(group_name=group_name, user_id=user_id)  # 設置 user_id
        db.session.add(new_item)
        db.session.commit()
        
        # 重定向到首頁或其他頁面
        return redirect(url_for('terminal'))

@app.route('/create_term', methods=['POST'])
def create_term():
    if request.method == 'POST':
        data = request.json
        term_id = data.get('term_id')
        term_name = data.get('term_name')
        city = data.get('city')
        group_id = data.get('group_id')
        if group_id == "":
            group_id = None 
        new_term = Term_mange(term_id=term_id ,term_name=term_name, city=city ,group_id=group_id)
        db.session.add(new_term)
        db.session.commit()
    return redirect(url_for('terminal'))

@app.route('/delete_groups', methods=['POST'])
def delete_groups():
    if request.method == 'POST':
        group_ids = request.json
        for group_id in group_ids:
            group = Terms.query.get(group_id)
            if group:
                db.session.delete(group)
        db.session.commit()
    return redirect(url_for('terminal'))

@app.route('/delete_devices', methods=['POST'])
def delete_devices():
    data = request.get_json()
    device_ids = data.get('device_ids', [])

    if not device_ids:
        return jsonify({"success": False, "error": "No device IDs provided"}), 400

    try:
        # 删除对应设备的记录
        for device_id in device_ids:
            term = Term_mange.query.filter_by(term_id=device_id).first()
            if term:
                db.session.delete(term)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500   

@app.route('/get_term_info', methods=['POST'])
def get_term_info():
    if request.method == 'POST':
        id = request.json['id']
        try:
            term = Term_mange.query.filter_by(id=id).first()
            if term:
                return jsonify({
                    'term_id': term.term_id,
                    'term_name': term.term_name,
                    'city': term.city
                })
            else:
                return jsonify({'error': 'Term not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/user')
@login_required
def user():
    if current_user.authority == 'admin':
        users = User.query.all()  # Admin can see all users

        # Move admin to the top of the list
        users = sorted(users, key=lambda u: u.authority != 'admin')
        
        show_add = True
        show_edit = True
        show_delete = True
    elif current_user.authority == 'root':
        users = [current_user]  # Root user can only see their own data
        show_add = False
        show_edit = False
        show_delete = False
    else:
        users = [current_user]  # Fallback if needed
        show_add = False
        show_edit = False
        show_delete = False

    return render_template('user.html', users=users, show_add=show_add, show_edit=show_edit, show_delete=show_delete)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if current_user.authority != 'admin':
        flash('Permission denied: You do not have the necessary privileges to add users.', 'error')
        return redirect(url_for('user'))

    if request.method == 'POST':
        username = request.form.get('username')
        account = request.form.get('account')
        password = request.form.get('password')
        ip = request.form.get('ip')
        authority = request.form.get('authority')
        email = request.form.get('email')
        address = request.form.get('address')

        # Add new user to database
        user = User(username=username, account=account, password=password, ip=ip, authority=authority, email=email, address=address)
        db.session.add(user)
        db.session.commit()
        
        flash('User added successfully.', 'success')
        return redirect(url_for('user'))
    return render_template('add.html')

@app.route('/delete')
def delete():
    if current_user.authority != 'admin':
        flash('Permission denied: You do not have the necessary privileges to delete users.', 'error')
        return redirect(url_for('user'))

    username = request.form.get('username')
    user_to_delete = User.query.filter_by(username=username).first()

    # Ensure the user exists and admin is not deleting themselves
    if user_to_delete and user_to_delete != current_user:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    else:
        flash('Cannot delete the specified user.', 'error')

    return redirect(url_for('user'))

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    username = request.args.get('username')
    user = User.query.filter_by(username=username).first()

    # Only admin or the user themselves can edit their information
    if user and (current_user.authority == 'admin' or user == current_user):
        if request.method == 'POST':
            user.username = request.form.get('username')
            user.account = request.form.get('account')
            user.password = request.form.get('password')
            user.ip = request.form.get('ip')
            user.authority = request.form.get('authority')
            user.email = request.form.get('email')
            user.address = request.form.get('address')
            db.session.commit()
            flash('User updated successfully.', 'success')
            return redirect(url_for('user'))
        return render_template('edit.html', user=user)
    
    flash('Permission denied: You do not have the necessary privileges to edit this user.', 'error')
    return redirect(url_for('user'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
