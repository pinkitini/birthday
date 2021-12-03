""" This handles all database communication"""
import datetime

from sqlalchemy.orm import backref

from projectapp import db

guest_gift = db.Table('guest_gift',
db.Column('guest_id', db.Integer, db.ForeignKey('guest.id')),
db.Column('gift_id', db.Integer, db.ForeignKey('gift.id')),db.Column('qty',db.Integer() ))

class Transaction(db.Model):
    trx_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    trx_guestid = db.Column(db.Integer(),db.ForeignKey('guest.id'), nullable=False)
    trx_amt = db.Column(db.Float(), nullable=False)
    trx_status = db.Column(db.String(40), nullable=False)
    trx_others = db.Column(db.String(255), nullable=True)
    trx_ref= db.Column(db.String(12), nullable=False)
    trx_ipaddress=db.Column(db.String(20), nullable=True)
    trx_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)    

    #set relationship
    guest=db.relationship("Guest",backref="guesttrx")

class Lga(db.Model):
    lga_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    state_id=db.Column(db.Integer(),db.ForeignKey('state.state_id'))
    lga_name = db.Column(db.String(55), nullable=False) 

class State(db.Model):
    state_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    state_name = db.Column(db.String(55), nullable=False) 


class Question(db.Model):
    q_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    guest_id=db.Column(db.Integer(),db.ForeignKey('guest.id'))
    question = db.Column(db.String(255), nullable=False) 
    doc_date=db.Column(db.DateTime(), default=datetime.datetime.utcnow) 
    #set relationship
    questioner=db.relationship('Guest',back_populates='questions')  

class Guest(db.Model):
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    fname = db.Column(db.String(55), nullable=False)
    lname = db.Column(db.String(55), nullable=False)
    email = db.Column(db.String(55), nullable=False)
    profile_pix = db.Column(db.String(100), nullable=True)
    pwd = db.Column(db.String(255), nullable=False) 
    stateid=db.Column(db.Integer(),db.ForeignKey('state.state_id'))
    datereg=db.Column(db.DateTime(), default=datetime.datetime.utcnow)   
    #set up relationship with gift
    gifts= db.relationship('Gift',secondary=guest_gift, backref='dguest')
    #set relationship
    questions=db.relationship('Question',back_populates='questioner') 

class Document(db.Model):
    doc_id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    doc_filename = db.Column(db.String(55), nullable=False)
    doc_message = db.Column(db.String(200), nullable=True)
    doc_date=db.Column(db.DateTime(), default=datetime.datetime.utcnow)   

class Gift(db.Model):
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    gift_name = db.Column(db.String(55), nullable=False) 

