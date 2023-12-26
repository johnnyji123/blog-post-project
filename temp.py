import mysql.connector
from flask import Flask, url_for, request, render_template




db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "projects123123",
        database = "blog_posts_db"
    )


cursor = db.cursor()


# table blog_posts


app = Flask(__name__)


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
    
    return render_template("post_blog.html")


if __name__ == ("__main__"):
    app.run(debug = True, use_reloader = False)