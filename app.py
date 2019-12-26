from flask import Flask, render_template, redirect, flash, request, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import sys
import click


WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


app = Flask(__name__)
# 初始化扩展，传入程序实例
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# 设置签名所需的密钥
app.config['SECRET_KEY'] = 'dev'
# 实例化扩展类
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@app.route('/')
def user_page():
    if request.method == 'POST':
        if not current_user.is_authenticated:  # 如果当前用户未认证
            return redirect(url_for('user_page'))  # 重定向到主页
    movies = Movies.query.all()
    return render_template('index.html', movies=movies)


@app.route('/movies/edit', methods=['GET', 'POST'])
def edit_page():
    """
    添加信息
    """
    if request.method == 'POST':
        title = request.form.get('title')
        chinese = request.form.get('chinese')
        image_url = request.form.get('image_url')
        if not title or not chinese:
            flash('Invalid input.')
            return redirect(url_for('edit_page'))  # 重定向回主页面
        # 保存表单数据到数据库
        movie_new = Movies(title=title, chinese=chinese, image_url=image_url)
        db.session.add(movie_new)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('edit_page'))
    movies = Movies.query.all()
    return render_template('edit.html', movies=movies)


@app.route('/movies/edit/alter/<int:movie_id>', methods=['POST', 'GET'])
def alter_page(movie_id):
    """
    修改信息
    """
    movie = Movies.query.get_or_404(movie_id)
    if request.method == 'POST':
        title = request.form['title']
        chinese = request.form['chinese']
        image_url = request.form['image_url']
        if not title or not chinese:
            flash('Invalid input.')
            return redirect(url_for('alter_page', movie_id=movie_id))  # 重定向回编辑页面
        # 保存表单数据到数据库
        movie.title = title
        movie.chinese = chinese
        movie.image_url = image_url
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('edit_page'))
    return render_template('alter.html', movie=movie)


@app.route('/movies/edit/delete/<int:movie_id>', methods=['POST', 'GET'])
@login_required  # 登录保护
def delete(movie_id):
    """
    删除信息
    """
    movie = Movies.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item delete')
    return redirect(url_for('edit_page'))


@app.route('/user/login', methods=['POST', 'GET'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login_page'))
        user = User.query.first()
        # 进行验证
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success')
            return redirect(url_for('user_page'))
        flash('Invalid username or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('login_page'))  # 重定向回登录页面
    return render_template('login.html')


@app.route('/user/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye')
    return redirect(url_for('user_page'))


@app.route('/user/settings', methods=['POST', 'GET'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']
        if not name or len(name) > 20:
            flash('Invalid name')
            redirect(url_for('settings'))
        current_user.name = name
        db.session.commit()
        flash('Setting update')
        return redirect(url_for('user_page'))
    return render_template('settings.html')


@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):
    return render_template('404.html'), 404


# 由于404页面和index页面中都需要传入user变量，进行优化
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))  # 用户名
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    chinese = db.Column(db.String(60))
    image_url = db.Column(db.String(200))


@app.cli.command(with_appcontext=False)  # 注册命令
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database')


@app.cli.command()
def forge():
    db.create_all()
    name = 'Rico'
    movies = [
        {'title': 'Game of Thrones', 'chinese': '权力的游戏',
         'image_url': 'http://5b0988e595225.cdn.sohucs.com/images/20190520/8bc1c0894ae842ab8d03710ee4163819.jpeg'},
        {'title': 'Westworld', 'chinese': '西部世界',
         'image_url': 'https://imgcdn.91pic.org/img/poster/4b024f6db415f3a3.jpg'},
        {'title': 'Vikings', 'chinese': '维京传奇',
         'image_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcThRSDGWtb3q-rPqEbok0SzEBOHWD7rsLPlTKOvWZNUaRIu5p56&s'},
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movies(title=m['title'], chinese=m['chinese'], image_url=m['image_url'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Done.')


@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user"""
    db.create_all()
    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo('Done.')


if __name__ == '__main__':
    app.run(Debug=True)
