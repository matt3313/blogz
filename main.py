
from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '8h15lf'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    text = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, text, owner):
        self.title = title
        self.text = text
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref = 'owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/index')
def index():
    blog = Blog.query.all()
    user = User.query.all()
    blog_id = request.args.get('id')
    return render_template('index.html', title = 'Blogz', user=user, blog=blog)        

@app.route("/blog", methods=['GET', 'POST'])
def blog():
    blog_id = request.args.get('id')
    if (blog_id):
        blog = Blog.query.get(blog_id)
        return render_template('single-blog.html', title="Blogz", blog=blog)

    blogs = Blog.query.all()

    return render_template("blog.html", title = "Blogz", blogs = blogs)


@app.route("/newpost", methods = ['GET', 'POST'])
def newpost():

    
    if request.method == 'POST':
        
        new_title = request.form['title']
        new_text = request.form['text']
        
        title_error = ''
        text_error = ''
        
        if len(new_title) < 1:
            title_error = 'Please enter a title'

        if len(new_text) < 1:
            text_error = 'Please enter text'
        
        if not text_error and not title_error:
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(new_title, new_text, owner)
            db.session.add(new_blog)
            db.session.commit()
            blog_id = str(new_blog.id)
            query_str = '/blog?id=' + blog_id
            return redirect(query_str)

        else:
            return render_template('newpost.html', title_error = title_error, text_error = text_error, new_text = new_text)
        
    else:
        return render_template("newpost.html", title = 'Blogz')


@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
    else:
        return render_template('login.html')

@app.route("/logout")
def logout():
    if session:
        del session['username']
        return redirect('/blog')
    else:
        return redirect('/blog')


def is_empty(field):
    if len(field) < 1:
        return True
    else:
        return False

def is_space(field):
    if ' ' in field:
        return True
    else:
        return False


@app.route("/signup", methods = ['GET', 'POST'])
def validate_form():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['password1']
        error_user_name = ''
        password_error = ''
        password_error1 = ''
        invalid_username = 'Thats not a valid user name'
        invalid_password = 'Thats not a valid password'
        existing_user = User.query.filter_by(username=username).first()

        if is_empty(username):
            error_user_name = invalid_username

        if is_space(username):
            error_user_name = invalid_username

        elif len(username) < 3 or len(username) > 20:
            error_user_name = invalid_username

        if is_space(password):
            password_error = invalid_password

        if is_space(verify_password):
            password_error1 = invalid_password

        if len(password) < 3 or len(password) > 20:
            password_error = invalid_password
            password = ''
            verify_password = ''

        if is_empty(verify_password):
            password_error1 = invalid_password

        if is_space(verify_password):
            password_error1 = invalid_password

        if len(password) < 3 or len(password) > 20:
            password_error = invalid_password
            password = ''
            verify_password = ''

        elif password != verify_password:
            password_error = 'Passwords do not match'
            password_error1 = 'Passwords do not match'
            password = ''
            verify_password = ''

        if existing_user:
            error_user_name = "Username already exists"


        if not error_user_name and not password_error and not password_error1:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
            

        else:
            return render_template('signup.html', error_user_name=error_user_name, user_name=username, \
            password_error = password_error, password_error1 = password_error1)
    else:
        return render_template("signup.html")


if __name__ == '__main__':
    app.run()