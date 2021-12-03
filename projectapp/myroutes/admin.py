import os, random
from flask import render_template,url_for,session,flash,redirect,request

from projectapp import app,db
from projectapp.mymodel import Guest,State, Document
from projectapp.forms import InvitationForm


@app.route('/admin/uploadiv', methods=['GET','POST'])
def uploadiv():
    form = InvitationForm()
    if request.method =='GET':
        return render_template('admin/ivform.html', form=form)
    else:
        #do validation here
        if form.validate_on_submit():
            message = request.form.get('message','No Info')
            uploaded_file = request.files['ivcard']
            
            #generate a random name and save with teh extension
            name, ext = os.path.splitext(uploaded_file.filename) #get ext
            
            newname = str(random.random() * 100000000) + ext #new random name
            destination = 'projectapp/static/docs/'+newname
            uploaded_file.save(destination)

            #To DO: insert newname,message into document table 
            doc = Document(doc_filename=newname,doc_message=message)
            db.session.add(doc)
            db.session.commit()

            flash("I.V Successfully uploaded")
            return redirect(url_for('dashboard'))
        else:
            return render_template('admin/ivform.html', form=form)
            



@app.route('/admin/delete/<int:guestid>')
def delete(guestid):
    x = db.session.query(Guest).get(guestid)
    db.session.delete(x)
    db.session.commit()
    #redirect
    flash('User Deleted')
    return redirect(url_for('allguests'))



@app.route('/admin/dashboard/')
def dashboard():
    #get the count from guest table
    guests = db.session.query(Guest).count()
    return render_template('admin/dashboard.html', guests=guests)

@app.route('/admin/guests')
def allguests():
    #HERE get the lists of all our guests and pass it to the template
    all = db.session.query(Guest).all()
    #method1
    data = db.session.query(Guest,State).join(State).all()
    #method 2:
    data =Guest.query.join(State).add_columns(State).all()

    return render_template('admin/admin.html',all=all, data=data)
    #Link the dashboard Guest Count to this route
    






@app.route('/admin')
def adminhome(): 
    return render_template('admin/admin_layout.html')

@app.route('/login')
def adminabout(): 
    return render_template('admin/adminpage.html')