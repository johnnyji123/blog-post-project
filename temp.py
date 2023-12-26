import mysql.connector
from flask import Flask, url_for, request, render_template, send_from_directory
import random
import uuid
from datetime import date
import sys
import os

db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "projects123123",
        database = "blog_posts_db"
    )


cursor = db.cursor()


# table blog_posts


app = Flask(__name__)
app.config['images'] = r'C:\Users\jj_jo\blog-post-project\Flask_app\images'

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


@app.route("/show_blogs", methods = ["GET", "POST"])
def show_blogs():
    query = cursor.execute("SELECT post_title, post_content, publication_date FROM blog_posts")
                           
    blog_data = render_dictionary(query)
    
    
    return render_template("show_blogs.html", blog_data = blog_data)


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





if __name__ == ("__main__"):
    app.run(debug = True, use_reloader = False) 



