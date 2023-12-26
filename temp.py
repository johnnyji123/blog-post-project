import mysql.connector
from flask import Flask, url_for, request




db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "projects123123",
        database = "blog_posts_db"
    )


cursor = db.cursor()


# table blog_posts


app = Flask(__name__)

def



if __name__ == ("__main__"):
    app.run(debug = True, use_reloader = False)