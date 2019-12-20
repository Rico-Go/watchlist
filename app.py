from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    return '<h1>Hello Rico!</h1><image src="http://wx4.sinaimg.cn/mw690/006HJgYYgy1fsnwktpl2fg305k05k49y.gif">'


@app.route('/page/')
def user_page():
    return render_template('index.html', name=name, movies=movies)


name = 'Rico'
movies = [
    {'title': 'Game of Thrones', 'chinese': '权力的游戏', 'image_url': 'http://5b0988e595225.cdn.sohucs.com/images/20190520/8bc1c0894ae842ab8d03710ee4163819.jpeg'},
    {'title': 'West world', 'chinese': '西部世界', 'image_url': 'https://imgcdn.91pic.org/img/poster/4b024f6db415f3a3.jpg'},
    {'title': 'Vikings', 'chinese': '维京传奇', 'image_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcThRSDGWtb3q-rPqEbok0SzEBOHWD7rsLPlTKOvWZNUaRIu5p56&s'},
]


if __name__ == '__main__':
    app.run()
