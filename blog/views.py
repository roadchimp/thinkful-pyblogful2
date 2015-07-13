from flask import render_template

from blog import app
from .database import session
from .models import Post


from flask import flash
from flask.ext.login import login_user
from werkzeug.security import check_password_hash
from .models import User

#verify login
from flask.ext.login import login_required

#find current user id
from flask.ext.login import current_user

#to logout user
from flask.ext.login import logout_user

@app.route("/")
@app.route("/page/<int:page>")
def posts(page=1, paginate_by=10):
    # Zero-indexed page
    page_index = page - 1

    count = session.query(Post).count()

    start = page_index * paginate_by
    end = start + paginate_by

    total_pages = (count - 1) / paginate_by + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    posts = session.query(Post)
    posts = posts.order_by(Post.datetime.desc())
    posts = posts[start:end]

    return render_template("posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages
    )
  
@app.route("/post/add", methods=["GET"])
@login_required
def add_post_get():
    return render_template("add_post.html")
  
import mistune
from flask import request, redirect, url_for

@app.route("/post/add", methods=["POST"])
@login_required
def add_post_post():
    post = Post(
        title=request.form["title"],
        content=mistune.markdown(request.form["content"]),
        author=current_user
    )
    session.add(post)
    session.commit()
    return redirect(url_for("posts"))

@app.route("/post/<int:id>", methods=["GET"])
@login_required
def view_post(id):
    posts = session.query(Post).get(id)
    return render_template("view_post.html",
         posts=posts        
    )
 
@app.route("/post/<int:id>/edit", methods=["GET"])
@login_required
def edit_post_get(id):
    posts = session.query(Post).get(id)
    return render_template("edit_post.html",
         posts=posts        
    )

@app.route("/post/<int:id>/edit", methods=["POST"])
@login_required
def edit_post_post(id):
    posts = session.query(Post).get(id)
    posts.title = title=request.form["title"]
    posts.content = mistune.markdown(request.form["content"])
    session.commit()
    return redirect(url_for("posts"))

@app.route("/post/<int:id>/delete")
@login_required
def delete_post_post(id):
    posts = session.query(Post).get(id)
    return render_template("delete_post.html",
           posts=posts     
    )
  
@app.route("/post/<int:id>/delete_confirm")
def delete_post_confirm(id):
    posts = session.query(Post).get(id)
    session.delete(posts)
    session.commit()
    return redirect(url_for("posts"))
    
@app.route("/register", methods=["GET"])
def register_get():
  return render_template("register.html")
from getpass import getpass
from werkzeug.security import generate_password_hash

@app.route("/register", methods=["POST"])
def register_post():
  print "In method post"
  name = request.form["username"]
  email = request.form["emailaddr"]
  if session.query(User).filter_by(email=email).first():
    flash("User email exists, please login")
    return redirect(url_for("login_get"))
  print "Checking passwords"
  password1=request.form["password1"]
  password2=request.form["password2"]
  print "Checking passwords{} and {}".format(password1, password2)
  if not (password1 and password2 ) or (password1 != password2):
    flash("passwords do not match please attempt again")
    print "Passwords do not match"
    return redirect(url_for("register"))
    
  user = User(name=name, email=email, password =generate_password_hash(password1))
  session.add(user)
  session.commit()
  print "Redirecting to posts"
  return redirect(url_for("login_get"))
  
@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")
  
@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("posts"))

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("posts"))