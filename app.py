from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
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


@app.route('/')
def user_page():
    movies = Movies.query.all()
    return render_template('index.html', movies=movies)


@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):
    return render_template('404.html'), 404


# 由于404页面和index页面中都需要传入user变量，进行优化
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)



class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Movies(db.Model):
    mid = db.Column(db.Integer, primary_key=True)
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
        {'title': 'West world', 'chinese': '西部世界',
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


if __name__ == '__main__':
    app.run(Debug=True)
