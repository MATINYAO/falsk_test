from calendar import prmonth
import sqlite3
from flask import Flask,render_template
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click
from flask import request, url_for, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin
from flask_login import login_user
from flask_login import login_required, current_user


app = Flask(__name__)
db = SQLAlchemy(app)
#@app.route('/')
#@app.route('/index')
#def hello():
#    return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)


class User(db.Model):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 名字


class Movie(db.Model):  # 表名将会是 movie
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份
    

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))     #用户名
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    username = db.Column(db.String(128))    # 密码散列值
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)    #返回布尔值
    

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))
    return user
    
    
    


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')
    

@app.cli.command()

def forge():
    """Generate fake data."""
    db.create_all()

    # 全局的两个变量移动到这个函数内
    #name = 'Martin Ding'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    
    # user = User(name=name)
    # db.session.add(user)
    
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)


        
    db.session.commit()
    click.echo('Done.')


#@app.route('/')
#def index():
#    return render_template('index.html', name=name, movies=movies)


#@app.route('/user/<name>')
#def user_page(name):
#    return f'User: {escape(name)}'


@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page', name='greyli'))
    print(url_for('user_page', name='peter'))
    print(url_for('test_url_for', num=2))
    return 'Test page'


# name = 'Martin Ding'
# movies = [
#     {'title': 'My Neighbor Totoro', 'year': '1988'},
#     {'title': 'Dead Poets Society', 'year': '1989'},
#     {'title': 'A Perfect World', 'year': '1993'},
#     {'title': 'Leon', 'year': '1994'},
#     {'title': 'Mahjong', 'year': '1996'},
#     {'title': 'Swallowtail Butterfly', 'year': '1996'},
#     {'title': 'King of Comedy', 'year': '1999'},
#     {'title': 'Devils on the Doorstep', 'year': '1999'},
#     {'title': 'WALL-E', 'year': '2008'},
#     {'title': 'The Pork of Music', 'year': '2012'},
# ]


@app.errorhandler(404)   #传入要处理的错误代码
def page_not_found(e):
    user = User.query.first()
    return render_template('404.html', user=user)


@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# @app.route('/')
# def index():
#     movies = Movie.query.all()
#     return render_template('index.html', movies=movies)



@app.route('/', methods=['GET', 'POST'])
def index():
    # movies = Movie.query.all()
    if request.method == 'POST':
        title = request.form.get('title') # 传入表单对应输入字段的 name 值
        year = request.form.get('year')
        
        if not title or not year or len(year) >4 or len(title) > 60:
            flash('Invalid input')
            return redirect(url_for('index'))
        
        #否则追加到数据库中
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        
        flash('Item created.')
        return redirect(url_for('index'))
    
        movies = Movie.query.all()
    return render_template('index.html', movies=movies)


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':  # 处理编辑表单的提交请求
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面

        movie.title = title  # 更新标题
        movie.year = year  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页

    return render_template('edit.html', movie=movie)  # 传入被编辑的电影记录
        


#删除
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])  # 限定只接受 POST 请求
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)  # 获取电影记录
    db.session.delete(movie)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index'))  # 重定向回主页




@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    
    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username = username, name='Admin')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()  # 提交数据库会话
    click.echo('Done.')
    
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))
        
        
        user = User.query.first()
        #验证用户名和密码是否一致
        
        if username == user.username and user.validate_password(password):
            login_user(user) #登入用户
            flash('Login success.')
            return redirect(url_for('index'))
            #重定向到修改页面
            
        flash('Invalid username or password.')
        return redirct(url_for('login'))
    
    return render_template('login.html')



from flask_login import login_required, logout_user

# ...

@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))  # 重定向回首页



@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required  # 登录保护
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')