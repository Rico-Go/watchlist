from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return '<h1>Hello Rico!</h1><image src="http://wx4.sinaimg.cn/mw690/006HJgYYgy1fsnwktpl2fg305k05k49y.gif">'


@app.route('/user/<name>')
def user_page(name):
    return 'Hello %s' % name


if __name__ == '__main__':
    app.run()
