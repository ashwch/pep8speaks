# -*- coding: utf-8 -*-
import builtins
import hmac
import os
import sys
import urllib.parse as urlparse
from flask import Flask, render_template, redirect, request
from flask_session import Session
import psycopg2
from pep8speaks import handlers, helpers


# For running locally without connecting to the database
if "OVER_HEROKU" in os.environ:
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["DATABASE_URL"])

    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

    cursor = conn.cursor()

    # Make the objects available across all the modules
    builtins.conn = conn
    builtins.cursor = cursor


app = Flask(__name__)
sess = Session()


@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == "GET":
        return redirect("https://pep8speaks.com")
    elif request.method == "POST":
        # GitHub sends the secret key in the payload header
        if helpers.match_webhook_secret(request):
            event = request.headers["X-GitHub-Event"]
            if event == "pull_request":
                return handlers.handle_pull_request(request)
            elif event == "pull_request_review":
                return handlers.handle_review(request)
            elif event == "pull_request_review_comment":
                return handlers.handle_review_comment(request)
            elif event == "integration_installation":
                return handlers.handle_integration_installation(request)
            elif event == "integration_installation_repositories":
                return handlers.handle_integration_installation_repo(request)
    else:
        return render_template('index.html')


app.secret_key = os.environ["APP_SECRET_KEY"]
app.config['SESSION_TYPE'] = 'filesystem'

sess.init_app(app)
app.debug = False

if __name__ == '__main__':
    app.run(debug=True)
