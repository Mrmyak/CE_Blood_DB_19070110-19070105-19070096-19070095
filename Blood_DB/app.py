#import os
from authy.api import AuthyApiClient
from flask import (Flask, Response, request, redirect, jsonify ,config ,
    render_template, session, url_for)

from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
from flask import current_app as app
from flask_cors import CORS, cross_origin
from config import *


app = Flask(__name__)

cors = CORS(app)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sql6405560:PldU8JWd3l@sql6.freemysqlhosting.net:3306/sql6405560'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mahesh789@localhost:3306/blood_db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False


ma = Marshmallow(app)
db = SQLAlchemy(app)





class User(db.Model):
    __tablename__ = "User"
    ID = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(80), nullable=False)
    dob=db.Column(db.String(20) , nullable=True)
    blood_group=db.Column(db.String(10), nullable= False )
    sex = db.Column(db.String(120), nullable=True)
    province = db.Column(db.String(120), nullable=False)
    district = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=True)
    date_created= db.Column(db.String(120), default =datetime.utcnow())
    phone_number=db.Column(db.BigInteger(),unique=False,primary_key=True)
    def __init__(self, fullname,dob, blood_group, sex, province,district, email, date_created,phone_number):
        self.fullname=fullname
        self.blood_group=blood_group
        self.sex=sex
        self.dob=dob
        self.province=province
        self.district=district
        self.email=email
        self.date_created=date_created
        self.phone_number=phone_number
        

class UserSchema(ma.Schema):
    class Meta:
        fields=('fullname','blood_group','sex','province','district' ,'email','phone_number')

#initialise schema
user_schema=UserSchema()
users_schema=UserSchema(many=True)



app.config.from_object('config')

app.secret_key = app.config['SECRET_KEY']
api = AuthyApiClient(app.config['AUTHY_API_KEY'])


@cross_origin()
@app.route("/", methods=["GET", "POST"])
@app.route("/phone_verification", methods=["GET", "POST"])
@app.route("/edit", methods=["GET", "POST","DELETE"])
def phone_verification():
    if request.method == "POST":
        country_code = request.form.get("country_code")
        phone_number = request.form.get("phone_number")
        method = request.form.get("method")

        session['country_code'] = country_code
        session['phone_number'] = phone_number

        api.phones.verification_start(phone_number, country_code, via=method)

        return redirect(url_for("verify"))

    return render_template("phone_verification.html")


@app.route("/verify", methods=["GET", "POST"])
@cross_origin()
def verify():
    if request.method == "POST":
            token = request.form.get("token")

            phone_number = session.get("phone_number")
            session["phone_number"]=phone_number
            country_code = session.get("country_code")

            verification = api.phones.verification_check(phone_number,
                                                         country_code,
                                                         token)

            if verification.ok():
                return redirect(url_for("register"))

    return render_template("verify.html")


@app.route("/register", methods=["GET","POST"])
@cross_origin()
def register():
    users=None
    try:
        
        fullname = request.form.get("fullname")

        
        dob=request.form.get("dateofbirth")
        blood_group=request.form.get("rating")
        sex= request.form.get('options')
        
     
        province=str(request.form.get('province_select')) 
        district=str(request.form.get('district_ID'))
        
        email=request.form['email']
        now=datetime.now()
        date_created = now.strftime("%d/%m/%Y %H:%M:%S")
        
        phone_number = session.get("phone_number")
        if phone_number is None:
            phone_number = '123'
        
        
        new_user = User(fullname,dob, blood_group, sex, province,district, email, date_created ,phone_number)
        
        db.session.add(new_user)  # Adds new User record to database
        db.session.commit()
    
        
        return user_schema.jsonify(new_user)
        
    except Exception as e:
        print(e)
        return(render_template("registerpage.html"))
    users=User.query.all()
    return redirect(url_for("register"))


@app.route("/users", methods=["GET"])
@cross_origin()
def getusers():
    users=User.query.all()
    return users_schema.jsonify(users)


@app.route('/user', methods=['GET'])
@cross_origin()   
def get_usersquery(): 
    reqArgs = request.args
    query = User.query
    if "type" in reqArgs:
        query = query.filter(User.blood_group == reqArgs.get("type"))
    if "dis" in reqArgs:
        query = query.filter(User.district == reqArgs.get("dis"))
    if "prov" in reqArgs:
        query = query.filter(User.province == reqArgs.get("prov"))
    
    result = users_schema.dump(query)

    return jsonify(result)

@app.route("/search", methods=["GET"])

@cross_origin()
def search():
    return(render_template("search.html"))


@cross_origin()
@app.route("/edit", methods=["GET", "POST"])
def edit():
    return(render_template("edit.html"))




@app.route("/aboutus", methods=["GET"])
def aboutus():
    return(render_template("aboutus.html"))

@app.route('/delete/<string:ID>', methods=["POST","DELETE"])
def delete():
    cur =mysql.connect.cursor()
    cur.execute("DELETE FROM user WHERE ID=%s",(ID))
    
    mysql.connection.commit()  
    result = users_schema.dump(query)
    return jsonify(result) 

if __name__ == '__main__':
    app.run(debug=True)




