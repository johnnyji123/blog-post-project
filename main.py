import mysql.connector
from flask import Flask, url_for, request, render_template, send_from_directory, flash, redirect, url_for
import random
import uuid
from datetime import date
import sys
import os
import string
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Connecting to database
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


# Function to render columns and values in database
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

    
    
    
# Endpoint that handles inserting information into database
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



# Endpoint that displays blog information on front page
@app.route("/", methods = ["GET", "POST"])
@login_required
def home_page():
    query = cursor.execute("SELECT post_id, author_id, post_title FROM blog_posts")
    post_title = render_dictionary(query)
    
    return render_template("home_page.html", post_title = post_title)




# Endpoint that passes down the images directory
@app.route("/images/<filename>")
def render_images(filename):
    return send_from_directory(app.config['images'], filename)

    


# Endpoint that takes you to the blog page based on post_id
@app.route("/view_blog/<post_id>", methods = ["GET", "POST"])
def view_blog(post_id):
    query = cursor.execute("SELECT post_id, post_title, post_content, author_id, publication_date FROM blog_posts WHERE post_id = %s",
                           (post_id, ))
    

    render_data = render_dictionary(query)
    
    cursor.execute("SELECT file_path FROM blog_posts")

    for file in cursor:
        file_path = file[0]
        extract_name = os.path.basename(file_path)
        
        
    user_comment = cursor.execute("SELECT post_id, comment_id, username, content, timestamp FROM comments WHERE post_id = %s",
                   (post_id, ))
    
    user_details = render_dictionary(user_comment)
       
    
    return render_template("view_blog.html", data = render_data, filename = extract_name, user_details = user_details)    



# User class to handle logged in user
class User(UserMixin):
    def __init__(self, email, password, user_id):
        self.email = email
        self.password = password
        self.id = user_id



# Loading user from database
@login_manager.user_loader
def load_user(user_id):
    cursor.execute("SELECT email, password, user_id FROM user WHERE user_id = %s", (user_id, ))
    user_details = cursor.fetchone()
    
    return User(*user_details, )



# Check if email and password mtaches the values in the database
@app.route("/login", methods = ["GET", "POST"])
def check_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        cursor.execute("SELECT email, password, user_id FROM user WHERE email = %s ", (email, ))
        user_details = cursor.fetchone()
       
        if email == user_details[0] and password == user_details[1]:
            user = User(*user_details, )
            login_user(user)
            return redirect(url_for('home_page'))
        
        else:
            flash("Wrong email or password")
            return render_template("login.html")
    
    return render_template("login.html")    
            


# Endpoint that logs out the user
@app.route("/logout", methods = ["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for('check_login'))



# Add comments based on post id
@app.route("/add_comment/<post_id>", methods = ["GET", "POST"])
def add_comment(post_id):
    comment_id = "".join(random.choices(string.ascii_lowercase, k = 5))
    user_email = current_user.email
    comment = request.form.get("content")
    timestamp = date.today()


    
    cursor.execute("INSERT INTO comments (comment_id, post_id,  username, content, timestamp) VALUES (%s, %s, %s ,%s, %s) ",
                   (comment_id, post_id, user_email, comment, timestamp ))
    
    
    db.commit()
    
      
    
    return redirect(url_for('view_blog', post_id = post_id))
    


# Delete comment based on post id and comment id 
@app.route("/delete_comment/<post_id>/<comment_id>", methods = ["GET", "POST"])
def delete_comment(post_id, comment_id):
    cursor.execute("DELETE FROM comments WHERE post_id = %s AND comment_id = %s",
                   (post_id, comment_id))
    
    
    db.commit()
    return redirect(url_for('view_blog', post_id = post_id))


# Redirect to edit_post page
@app.route("/update_post", methods = ["GET", "POST"])
def update_post_page():
    return render_template("edit_post.html")



# Edit blog post values
@app.route("/edit_post/<post_id>", methods = ["GET", "POST"])
def edit_post(post_id):
    current_date = date.today()
    post_title = request.form.get("post_title")
    post_content = request.form.get("post_content")
    
    if 'filename' in request.files:
        file = request.files['filename']
        
        if file:
            file_path = os.path.join(app.config['images'], file.filename)
            file.save(file_path)
            
    cursor.execute(
            """
            UPDATE blog_posts
            SET post_title = %s, post_content = %s, publication_date = %s, file_path = %s 
            WHERE post_id = %s
            """,
            (post_title, post_content, current_date, file_path, post_id)
        )
    
    db.commit()
    return redirect(url_for('edit_post', post_id = post_id))



if __name__ == ("__main__"):
    app.run(debug = True, use_reloader = False) 
    


