import mysql.connector
from flask import Flask, url_for, request, render_template
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
def show_blogs():
    query = cursor.execute("SELECT post_title, post_content, publication_date FROM blog_posts")
    blog_data = render_dictionary(query)
    

    
    return render_template("home_page.html", blog_data = blog_data)





if __name__ == ("__main__"):
    app.run(debug = True, use_reloader = False)



