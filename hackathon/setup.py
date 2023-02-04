import os
import pathlib
from user import *
import requests
from flask import Flask, session, abort, redirect, request, render_template
from google.oauth2 import id_token
from pip._vendor import cachecontrol
from google_auth_oauthlib.flow import Flow
from prof import store_email

import google.auth.transport.requests

app = Flask("Google Login App")
app.secret_key = "tarthack"
app.state = begin("data.txt")
 
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "518104372314-t2ko2vcps9ck39fkqq9u8knpissv4lpp.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")


flow = Flow.from_client_secrets_file(client_secrets_file = client_secrets_file, 
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri = "http://127.0.0.1:5000/callback"
                                    )


def login_is_required(function):
    def wrapper(*arg, **kwargs):
        if "google_id" not in session:
            return abort(401) #Auth Req
        else:
            return function()
    return wrapper

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)
    

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    
    if not session["state"] == request.args["state"]:
        abort(500)
    
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request = token_request,
        audience = GOOGLE_CLIENT_ID 
    )
    fname = id_info.get("given_name")
    lname = id_info.get("family_name")
    email = id_info.get("email")
    userDict = app.state.users
    usr = User(fname, lname, email)
    if usr not in userDict:
        app.state.addUser(usr)
        app.state.save()
    
    session["google_id"] = id_info.get("sub")
    session["mail"] = id_info.get("email")
    session["name"] = id_info.get("name")
    return redirect("/protected_area")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/")
def index():
    return render_template("website.html")

@app.route('/bio', methods = ['POST', 'GET'])
def data():
    email = session["mail"]
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        form_data = request.form
        print(form_data)
        if email in app.state.emailDict:
            print(form_data)
            for key in form_data:
                print(key)
            app.state.emailDict[email].addBio(form_data["bio"])
            app.state.save()
    redirect("/protected_area")
    return render_template('userprofile.html')
    
@app.route('/status', methods = ['POST', 'GET'])
def updateStatus():
    email = session["mail"]

    if request.method == 'GET':
        return "stop eating crayons "
        
    if request.method == 'POST':
        form_data = request.form
        print(form_data)
        if email in app.state.emailDict:
            print(form_data)
            for key in form_data:
                print(key)
            status = form_data["status"]
            # need to fix this so that status is dropdown
            # for now, True or False
            app.state.emailDict[email].setStatus(status)
            app.state.save()
        # return render_template('userprofile.html')
    redirect("/protected_area")
    return render_template('userprofile.html')




@app.route("/protected_area")
@login_is_required
def protected_area():
    # loads the user webpage
    return render_template("userprofile.html", name=session["name"])

#original code
#f"Hello {session['name']}! <br/> <a href='/logout'><button>Logout</button></a>"
   


if __name__ == "__main__":
    app.run(debug=True)