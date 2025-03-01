from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import CheckConstraint
from app import app

from werkzeug.security import generate_password_hash,check_password_hash


db=SQLAlchemy(app)





##models

class Admin(db.Model):
    username=db.Column(db.String(255),primary_key=True)
    password = db.Column(db.String(255), nullable=False)


# Customer Model
class Customer(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    passhash = db.Column(db.String(512), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    city=db.Column(db.String(50),nullable=False) 
    block=db.Column(db.Boolean, default=False) 
    
    @property
    def password(self):
        raise AttributeError("Password is not a readable property.")
    
    @password.setter
    def password(self,password):
        self.passhash=generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.passhash,password)
    
    # Relationships
    service_requests = db.relationship('ServiceRequest', backref='customer',lazy=True)
  
  
  
# Professional Model
class Professional(db.Model):
    prof_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50),  nullable=False)
    passhash = db.Column(db.String(512), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    service_type = db.Column(db.String(100), db.ForeignKey('service.name'), nullable=False)
    block=db.Column(db.Boolean, default=False) 

    experience = db.Column(db.Integer, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    verified = db.Column(db.Boolean, default=None,nullable=True)  # Approved by admin
    city=db.Column(db.String, nullable=False)
    
    # Storing the filename of the verification document
    verification_document = db.Column(db.String(255), nullable=True)
    
    @property
    def password(self):
        raise AttributeError("Password is not a readable property.")
    
    @password.setter
    def password(self,password):
        self.passhash=generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.passhash,password)

    # Relationships
    service_requests = db.relationship('ServiceRequest', backref='professional',lazy=True)
    
    def count_service_requests(self, status=None):
        if status:
            return len([req for req in self.service_requests if req.status == status])
        return len(self.service_requests)
  

   

# Service Model
class Service(db.Model):
    service_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False,unique=True)
    description = db.Column(db.Text, nullable=True)
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.String(50), nullable=True)

    # Relationships
    service_requests = db.relationship('ServiceRequest', backref='service',lazy=True)
    professionals = db.relationship('Professional', backref='service', lazy=True)
   



# Service Request Model
class ServiceRequest(db.Model):
    service_req_id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.service_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.prof_id'), nullable=False) 
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='requested')  # 'requested', 'assigned', 'closed'
    Address=db.Column(db.Text, nullable=True)
    offered_price=db.Column(db.Integer)
    rating = db.Column(db.Integer, nullable=True)
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('requested', 'assigned', 'closed','rejected')",
            name='check_service_request_status'
        ),
    )

  

 
with app.app_context():
    db.create_all()
    
    admin=Admin.query.filter_by(username='admin').first()
    if not admin:
        admin=Admin(username='admin',password="admin")
        db.session.add(admin)
        db.session.commit()
        