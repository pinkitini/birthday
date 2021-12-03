import random,os,string, json,requests
from flask import render_template,url_for,session,request, flash,redirect, abort

from flask import jsonify
from sqlalchemy.util.langhelpers import methods_equivalent

from werkzeug.security import generate_password_hash, check_password_hash


from projectapp import app, db
from projectapp.mymodel import State,Guest,Gift,guest_gift,Document,Question,Lga,Transaction


from projectapp import mail

from flask_mail import Message

# @app.route('/test')
# def testmail():
#     msg= Message(subject="Testing Mail", sender="sender@gmail.com", recipients=['moatacad@gmail.com'])
#     fp = open('requirements.txt')

#     msg.html = "<div><h1>Welcome on Board!</h1><p>You rae our greatest customer!</p><hr> Signed by Management<img src='https://cdn.britannica.com/q:60/91/181391-050-1DA18304/cat-toes-paw-number-paws-tiger-tabby.jpg' width='100%'></div>"
    
#     msg.attach("Requirements.txt", "application/text", fp.read())
#     mail.send(msg)
#     return "Mail was sent"



def refno():
    sample_xters = random.sample(string.digits,10) 
    joinedstring = ''.join(sample_xters)
    return joinedstring

@app.route('/user/paycash',methods=['GET','POST'])
def paycash():
    if session.get('user') !=None:
        if request.method =='GET':
            return render_template('user/cash_server1.html')
        else:
            guestid = session.get('user')
            amount=request.form.get("amount",0)

            #Generate a random string here,  save it in session. This is your transaction refrence

            ref = refno()
            session['trxref'] = ref

            #insert this into the transaction table
            t = Transaction(trx_guestid=guestid,trx_amt=amount,trx_status='Pending',trx_ref=ref) 
            db.session.add(t)
            db.session.commit()
            return redirect(url_for("confirmpay"))
    else:
        return redirect(url_for('login'))


@app.route('/user/confirmpay',methods=['GET','POST'])
def confirmpay():
    if session.get('user') !=None and session.get('trxref') !=None:
        ref = session.get('trxref')
        deets = db.session.query(Transaction).filter(Transaction.trx_ref==ref).first()

        if request.method=='GET':
            return render_template('user/confirmpay.html',deets=deets)  
        else:
            #connect to paystack endpoint
            amount = deets.trx_amt * 100
            email=deets.guest.email
            headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_3c5244cfb8965dd000f07a4cfa97185aab2e88d5"}            
            data = {"reference": ref, "amount": amount, "email": email}
            
            response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))

            rsp = json.loads(response.text) 
            if rsp.get('status') == True:
                payurl = rsp['data']['authorization_url']
                return redirect(payurl)
            else:
                return redirect(url_for('paycash'))
    else:     
        return redirect(url_for('login'))






@app.route('/user/available', methods=['GET','POST'])
def check_availability():
    if request.method =='GET':
        records = db.session.query(State).all()
        return render_template('user/test.html',records=records)
    else:#process ajax
        user=request.form.get('user')
        deets = db.session.query(Guest).filter(Guest.email==user).all()
        
        if deets:
            rsp = {"msg":"You have registered with this email", "status":"failed"}
            return jsonify(rsp)
        else:
            rsp = {"msg":"Username available", "status":"success"}
            return jsonify(rsp)

@app.route('/user/payverify')
def paystack():
    loggedin = session.get('user')
    refsession = session.get('trxref')
    if loggedin and refsession:
        #receive response from Payment Company and inform user of the transaction status
        ref=request.args.get('reference')

        headers = {'Authorization': 'Bearer sk_test_3c5244cfb8965dd000f07a4cfa97185aab2e88d5',}

        #urlverify = "https://api.paystack.co/transaction/verify/"+ref

        response = requests.get(f"https://api.paystack.co/transaction/verify/{ref}", headers=headers)
        
        rsp =response.json()#in json format
        #return render_template('user/test.html',rsp=rsp)

        if rsp['data']['status'] =='success':
            amt = rsp['data']['amount']
            ipaddress = rsp['data']['ip_address']
            t = Transaction.query.filter(Transaction.trx_ref==refsession).first()
            t.trx_status = 'Paid'
            db.session.commit()
            return "Payment Was Successful"
            #return 'update database and redirect them to the feedback page'
        else:
            t = Transaction.query.filter(Transaction.trx_ref==refsession).first()
            t.trx_status = 'Failed'
            db.session.commit()
            return "Payment Failed" 
    else:
        abort(403)

@app.route('/user/donatecash', methods=['GET','POST'])
def donatecash():
    loggedin = session.get('user')
    if loggedin:
        if request.method =='GET':
            #TO DO: create a html form like what is shown on the board
            return render_template('user/cash_1.html')
        else:
            #retrieve the data coming from the form and keep in a variable
            return "Form Submitted Here"
    else:
        abort(403)



        
        
   
@app.route('/user/lga')
def lga():
    state = request.args.get('stateid')
    data = db.session.query(Lga).filter(Lga.state_id==state).all()

    tosend = "<select class='form-control' name=''>"
    for t in data:
        tosend= tosend + f"<option>{t.lga_name}</option>"
    tosend=tosend+"</select>"

    return tosend



@app.route('/', methods=['GET','POST'])
def home(): 
    if request.method=='GET':    
        try:
            response = requests.get('http://127.0.0.1:5000/hostel/api/v1.0/listall/')
            hostels = json.loads(response.text) 		
            #response.json()
        except requests.exceptions.RequestException as e:
            hostels={}
            hostels['status'] = 0
        
        allstates = db.session.query(State).all()
        return render_template('user/home.html', allstates=allstates,hostels=hostels)
    else:
        #retrieve form data
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        email=request.form.get('email')
        password=request.form.get('password')
        state = request.form.get('state')
        #save into the database using ORM insert

        converted = generate_password_hash(password)

        g=Guest(fname=fname,lname=lname,email=email,pwd=converted,stateid=state)
        db.session.add(g)
        db.session.commit()
        #keep details in session
        session['user'] = g.id
        #save feedback in a flash and redirect to '/user/profile'
        flash('Registration was successful')        
        return redirect('/user/profile')

@app.route('/user/addpicture', methods=['GET','POST'])
def addpicture():
    if session.get('user') != None:
        if request.method=='GET':
            return render_template('user/upload.html')
        else: #form is submitted
            fileobj = request.files['pic']       

            if fileobj.filename == '':
                flash('Please select a file')
                return redirect(url_for('addpicture'))
            else:
                 #get the file extension,  #splits file into 2 parts on the extension
                name, ext = os.path.splitext(fileobj.filename)
                allowed_extensions=['.jpg','.jpeg','.png','.gif']

                if ext not in allowed_extensions:
                    flash(f'Extension {ext}is not allowed')
                    return redirect(url_for('addpicture'))
                else:
                    sample_xters = random.sample(string.ascii_lowercase,10) 
                    newname = ''.join(sample_xters) + ext

                    destination = 'projectapp/static/images/guest/'+newname
                    fileobj.save(destination)
                    ##save the details in the db
                    guestid = session.get('user')
                    guest = db.session.query(Guest).get(guestid)
                    guest.profile_pix=newname
                    db.session.commit() 
                    return redirect('/user/profile')
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')


@app.route('/user/login', methods=['GET','POST'])
def login():
    if request.method =='GET':
        #1. TO DO: display a template with login form
        return render_template('user/login.html')
    else:
        #2. TO DO: Retrieve form data
        username = request.form.get('username')
        pwd = request.form.get('pwd')
        #3. Write a query to fetch from the guest table where username='<formdata>' and pwd ='<formdata>'
        deets = db.session.query(Guest).filter(Guest.email==username).first()
        #4. if data was fetched, keep the id in session and redirect to profile page
        if deets:
            loggedin_user = deets.id
            hashedpass = deets.pwd
            check = check_password_hash(hashedpass, pwd)
            if check :
                session['user']= loggedin_user
                return redirect('/user/profile')
            else:
                flash('Invalid Credentials')
                return redirect(url_for('login'))
        else:
            #5. if data was empty, keep feedback in a flash and redirect to home page/login page (this same route)
            flash('Invalid Credentials')
            return redirect(url_for('login'))

@app.route('/user/gift', methods=['GET','POST'])
def gift():
    loggedin_user = session.get('user')
    if loggedin_user:
        if request.method == 'GET':
            allgifts = Gift.query.all() #db.session.query(Gift).all()
            
            guest = db.session.query(Guest).filter(Guest.id==loggedin_user).first() #Guest.query.get(loggedin_user)
            
            mygifts = guest.gifts # [<Gift1>,<Gift6>]
            mygiftlist= list()
            for i in mygifts:
                mygiftlist.append(i.id)

            return render_template('user/gift_registry.html',allgifts=allgifts, mygifts=mygiftlist)
        else:
            #retrieve form data
            #delete all the gifts being brought by this user
            db.session.execute(f"DELETE FROM guest_gift WHERE guest_id='{loggedin_user}'")
            selected = request.form.getlist('item')  #[2,4,5]
            if selected: 
                for t in selected:  #[2,4,5]
                    quantity = 'quantity_'+str(t) 
                    total = request.form.get(quantity,1)
                    statement = guest_gift.insert().values(gift_id=t, guest_id=loggedin_user,qty=total)
                    db.session.execute(statement)       
                db.session.commit() 
                flash('Thank you for your donation')
                return redirect('/user/profile')
            else:
                flash('Please select at least a gift item')
                return redirect('/user/gift')
    else:
        return redirect('/login')

@app.route('/user/ask-question')
def question():
    if session.get('user') != None:
        return render_template('user/questioner.html')
    else:
        return redirect(url_for('login'))


@app.route('/user/ask-question-ajax')
def questionajax():
    if session.get('user') != None:
        return render_template('user/questioner_ajax.html')
    else:
        return redirect(url_for('login'))

@app.route('/user/submitajax', methods=['GET','POST'])
def submitajax():    
    loggedin = session.get('user')
    if loggedin != None:
        quest = request.form.get('quest')
        firstn = request.form.get('fname')
        lastn = request.form.get('lname')
        csrf_token = request.form.get('csrf_token')
        pixobj = request.files['pix']
        filename = pixobj.filename
        #insert into db
        question = Question(guest_id=loggedin,question=quest)
        db.session.add(question)
        db.session.commit() 
        return f"Thank you {firstn} {lastn} , Your Question has been asked. The CSRF Token is {csrf_token} and the file is {filename}"
    else:
        return "You need to log in to ask a question"


@app.route('/user/submitquestion', methods=['POST'])
def submitquestion():    
    loggedin = session.get('user')
    if loggedin != None:
        quest = request.form.get('quest')
        #insert into db
        question = Question(guest_id=loggedin,question=quest)
        db.session.add(question)
        db.session.commit()
        flash('Thank you for asking')
        return redirect(url_for('userprofile'))
    else:
        return redirect(url_for('login'))
   
@app.template_filter()
def currencyFormat(value):
    value = float(value)
    return "{:,.2f}".format(value)

@app.route('/user/')        
@app.route('/user/profile')
def userprofile():
    loggedin_user = session.get('user')
    if loggedin_user != None:
        data = db.session.query(Guest).get(loggedin_user)
        iv = db.session.query(Document).get(1)
        return render_template('/user/profile.html', data=data,iv=iv)
    else:
        return redirect(url_for('login'))
 