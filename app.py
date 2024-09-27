import os
from datetime import datetime
from pymongo import MongoClient
from flask import Flask, render_template, request
from dotenv import load_dotenv


def create_app():
    app = Flask(__name__)
    client = MongoClient(os.getenv("MONGODB_URI"))
    app.db = client.db

    def get_title(text: str):

        # Get first sentence
        first_sentence = text.split("\n")[0]

        if first_sentence[0] == "#":
            title = first_sentence.strip("# ")
            text = text.split(first_sentence)[-1]
        else:
            title = text[:30] + "..."

        return title, text

    @app.route("/", methods=["GET", "POST"])
    def home():

        if request.method == "POST":
            entry_content = request.form.get("textarea")
            postted_date = datetime.today().strftime("%d-%m-%Y")
            app.db.my_blog_entries.insert_one(
                {"content": entry_content, "postted_date": postted_date}
            )

        entries = []

        for entry in app.db.my_blog_entries.find({}):
            title, content = get_title(entry["content"])
            entries.append(
                {
                    "title": title,
                    "datetime": entry["postted_date"],
                    "datetime_formatted": datetime.strptime(
                        entry["postted_date"], "%d-%m-%Y"
                    ).strftime("%b %d, %Y"),
                    "content": content,
                }
            )

        return render_template("home.html", entries=entries[::-1])

    return app


if __name__ == "__main__":
    load_dotenv()
    app = create_app()
    app.run()
