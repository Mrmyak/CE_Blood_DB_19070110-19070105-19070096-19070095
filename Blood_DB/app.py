
from authy.api import AuthyApiClient
from flask import (Flask, Response, request, redirect, jsonify ,config ,
    render_template, session, url_for)

from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
from flask import current_app as app
from flask_cors import CORS, cross_origin
from config import *
import random

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
    ID = db.Column(db.Integer,primary_key=True,autoincrement=True)
    fullname = db.Column(db.String(80), nullable=False)
    dob=db.Column(db.String(20) , nullable=True)
    blood_group=db.Column(db.String(10), nullable= False )
    sex = db.Column(db.String(120), nullable=True)
    province = db.Column(db.String(120), nullable=False)
    district = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=True)
    date_created=db.Column(db.String(120),default=datetime.utcnow())
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

class BloodRequest(db.Model):
    __tablename__ = "BloodRequest"
    ID = db.Column(db.Integer,primary_key=True,autoincrement=True)
    fullname = db.Column(db.String(80), nullable=False)
    don=db.Column(db.String(20) , nullable=True)
    blood_group=db.Column(db.String(10), nullable= False )
    #sex = db.Column(db.String(120), nullable=True)
    province = db.Column(db.String(120), nullable=False)
    district = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=True)
    
    message = db.Column(db.String(120), unique=False, nullable=True)
    purpose = db.Column(db.String(120), unique=False, nullable=False)
    units = db.Column(db.String(120), unique=False, nullable=False)
    age = db.Column(db.String(120), unique=False, nullable=False)
    location = db.Column(db.String(120), unique=False, nullable=False)
    hospital = db.Column(db.String(120), unique=False, nullable=True)
    
    date_created= db.Column(db.String(120), default =datetime.utcnow())
    phone_number=db.Column(db.BigInteger(),unique=False,primary_key=True)
    def __init__(self, fullname,don, blood_group, province,district, email,message,purpose,units,age,location,hospital, date_created,phone_number):
        self.fullname=fullname
        self.blood_group=blood_group
        self.don=don
        self.province=province
        self.district=district
        self.email=email
        self.message=message
        self.purpose=purpose
        self.units=units
        self.age=age
        self.location=location
        self.hospital=hospital
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
def verify():
    if request.method == "POST":
            token = request.form.get("token")

            phone_number = session.get("phone_number")
            session["phone_number"]=phone_number
            country_code = session.get("country_code")
            verification = api.phones.verification_check(phone_number,country_code,token)

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
        district=str(request.form.get('district_id'))
        print(district)
        
        email=request.form.get('email')
        now=datetime.now()
        date_created = now.strftime("%d/%m/%Y %H:%M:%S")
        
        phone_number = session.get("phone_number")
        if phone_number is None:
            phone_number = random.random()
            
        
        
        new_user = User(fullname,dob, blood_group, sex, province,district, email, date_created ,phone_number)
        
        db.session.add(new_user)  # Adds new User record to database
        print('new user added')
        db.session.commit()
        print("Commit")
        return user_schema.jsonify(new_user)
    
        
    except Exception as e:
        print(e)
        #return('Exception occured')
        return(render_template("registerpage.html"))
    users=User.query.all()
    #return redirect(url_for("register"))
    return "ERRORR"


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


@cross_origin()
@app.route("/bloodrequest", methods=["GET"])
def bloodrequestget():
    return(render_template("BloodRequest.html"))


@cross_origin()
@app.route("/bloodrequest", methods=["POST"])
def bloodrequest():
    users=None
    print("Hello naoao")
    try:

        fullname = request.form.get("fullname")
        don=request.form.get("don")
        blood_group=request.form.get("bloodgroup")
        province=str(request.form.get('province_select')) 
        district=str(request.form.get('district_ID'))
        email=request.form.get('email')
        now=datetime.now()
        date_created = now.strftime("%d/%m/%Y %H:%M:%S")
        phone_number = session.get("phone_number")
        if phone_number is None:
            phone_number = '123456'
        location =request.form.get('location')
        hospital=request.form.get('hospital')
        purpose=request.form.get('purpose')
        message=request.form.get('message')
        age=request.form.get('age')
        units=request.form.get('units')
        
        #fullname="Mahesh Dada"
        #don=121212
        #blood_group= "B+"
        #province="hahahaha"
        #district="bababab"
        #email="mahesbns@jaja.com"
        #location="Bagar"
        #purpose="Yesto Yesto vayooo :("
        #message="helppppppppppppppppp"
        #age=22
        #units= 23
        print('uew user aghi')
    
        new_user = BloodRequest(fullname,don, blood_group, province,district,email,message,purpose,units,age,location,hospital, date_created,phone_number)
        print("Hello before session")
        db.session.add(new_user)  # Adds new User record to database
        print("sessionpachi")
        db.session.commit()
        print("Commit pchi")
        return user_schema.jsonify(new_user)
        
    except Exception as e:
        print(e)
        return(render_template("errorpage.html"))
        users=User.query.all()
    return("Srror vayo dda")
    #return redirect(url_for("bloodrequest"))

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
    app.run(debug=True ,port="5000") 




