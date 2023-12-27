import mysql.connector
from flask import Flask, url_for, request, render_template, send_from_directory, flash, redirect, url_for
import random
import uuid
from datetime import date
import sys
import os
import string
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user




db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "projects123123",
        database = "blog_posts_db"
    )


cursor = db.cursor()
    

# table blog_posts
# table comments
# table user


app = Flask(__name__)
app.config['images'] = r'C:\Users\jj_jo\blog-post-project\Flask_app\images'
app.secret_key = "123123123"
login_manager = LoginManager(app)

def render_dictionary(query):
    col_names = [name[0] for name in cursor.description]
    data_lst = []
    
    all_rows = cursor.fetchall()
    
    for row in all_rows:
        row_dict = {}
        for col_name, value in zip(col_names, row):
            row_dict[col_name] = value
        data_lst.append(row_dict)
    
    return data_lst

    
    
    

@app.route("/post_blog", methods = ["GET", "POST"])
def post_blog():
    if request.method == "POST":
        title = request.form.get("post_title")
        content = request.form.get("post_content")
        post_id = uuid.uuid4()
        post_id_str = str(post_id)
        author_id = uuid.uuid4()
        author_id_str = str(author_id)
        publication_date = date.today()
        
        
        if 'filename' in request.files:
            file = request.files['filename']
            
            if file:
                file_path = os.path.join(app.config['images'], file.filename)
                file.save(file_path)
       
            
                    
        cursor.execute( 
                """
                INSERT INTO blog_posts
                (post_id, post_title, post_content, author_id, publication_date, file_path)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (post_id_str, title, content, author_id_str, publication_date, file_path)
            )                    
        
        db.commit()
        
        
    return render_template("post_blog.html")

@app.route("/", methods = ["GET", "POST"])
def home_page():
    query = cursor.execute("SELECT post_id, author_id, post_title FROM blog_posts")
    post_title = render_dictionary(query)
    
    return render_template("home_page.html", post_title = post_title)




@app.route("/images/<filename>")
def render_images(filename):
    return send_from_directory(app.config['images'], filename)

    


@app.route("/view_blog/<post_id>", methods = ["GET", "POST"])
def view_blog(post_id):
    query = cursor.execute("SELECT post_id, post_title, post_content, author_id, publication_date FROM blog_posts WHERE post_id = %s",
                           (post_id, ))
    

    render_data = render_dictionary(query)
    
    cursor.execute("SELECT file_path FROM blog_posts")

    for file in cursor:
        file_path = file[0]
        extract_name = os.path.basename(file_path)
        
        
    
    return render_template("view_blog.html", data = render_data, filename = extract_name)    



class User(UserMixin):
    def __init__(self, email, password, user_id):
        self.email = email
        self.password = password
        self.id = user_id



@app.route("/login", methods = ["GET", "POST"])
def check_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        cursor.execute("SELECT email, password, user_id FROM user WHERE email = %s ", (email, ))
        user_details = cursor.fetchone()
       
        if email == user_details[1] and password == user_details[2]:
            user = User(*user_details, )
            login_user(user)
            return redirect(url_for('home_page'))
        
        else:
            flash("Wrong email or password")
            return render_template("login.html")
    
    return render_template("login.html")    
            

@app.route("/logout", methods = ["GET", "POST"])
def logout():
    return redirect(url_for(''))



#if __name__ == ("__main__"):
    #app.run(debug = True, use_reloader = False) 



