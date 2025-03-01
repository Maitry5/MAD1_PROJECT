from functools import wraps
from flask import Flask,render_template,request,redirect,url_for,flash,session
from models import *
from app import app
import os
from werkzeug.utils import secure_filename
from datetime import date

UPLOAD_FOLDER = '/Users/maitry/mad1/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}


def auth_required(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if 'user_id' not in session:
            flash("You need to login first")
            return redirect(url_for('login'))
        return func(*args,**kwargs)
    return inner
        

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/login",methods=["POST"])
def login_post():
    username=request.form.get("username")
    password=request.form.get("password")
    usertype=request.form.get("usertype")
    
    
    if username=="" or password=="":
        flash("Username or Password can't be empty.")
        return redirect(url_for("login"))
    
    else:
        if usertype=="Customer":
            user=Customer.query.filter_by(username=username).first()
            if not user:
                flash("Customer profile doesn't exist")
                return redirect(url_for("login"))
            if not user.check_password(password):
                flash("Incorrect password")
                return redirect(url_for("login"))
            # if the login is succesful
            session['user_id']=user.customer_id
            customer_id=user.customer_id
            return redirect(url_for("customer_profile",customer_id=customer_id))
    
    
        if usertype=="Professional":
            user=Professional.query.filter_by(username=username).first()
            if not user:
                flash("Professional profile doesn't exist")
                return redirect(url_for("login"))
            if not user.check_password(password):
                flash("Incorrect password")
                return redirect(url_for("login"))
            # if the login is succesful
            session['user_id']=user.prof_id
            prof_id=user.prof_id
            return redirect(url_for("professional_profile", professional_id=prof_id))
        
        if usertype=="Admin":
            user=Admin.query.filter_by(username=username).first()
            if not user or not password==user.password:
                flash("Invalid credentials")
                return redirect(url_for("login"))
            session['user_id']=user.username
            return redirect(url_for("admin_home"))
              
        
@app.route('/logout')
@auth_required
def logout():
    session.pop('user_id',None)
    return redirect(url_for("login"))




############################# ADMIN ########################################

@app.route("/admin")
@auth_required
def admin_home():
    services=Service.query.all()
    return render_template("admin_home.html",services=services)

@app.route("/admin/requests")
@auth_required
def admin_requests():
    professionals = Professional.query.filter(Professional.verified == None).all()
    return render_template("admin_requests.html",professionals=professionals)



@app.route("/admin/search",methods=["GET","POST"])
@auth_required
def admin_search():
    if request.method=="GET":
        return render_template("admin_search.html")
    
    if request.method=="POST":
        parameter=request.form.get("parameter")
        query=request.form.get("query")
        if not parameter or not query:
            return render_template("admin_search.html")
        else:
            query_filter = Professional.query.filter(Professional.verified == True)
            professionals = []

            if parameter == "name":
                professionals = query_filter.filter(Professional.username.ilike(f"%{query}%")).all()
            elif parameter == "city":
                professionals = query_filter.filter(Professional.city.ilike(f"%{query}%")).all()
            elif parameter == "service_name":
                professionals = query_filter.filter(Professional.service_type.ilike(f"%{query}%")).all()
            elif parameter == "experience":
                professionals = query_filter.filter(Professional.experience >= query).all()
        
        return render_template("admin_search.html", professionals=professionals)


@app.route("/admin/summary")
@auth_required
def admin_summary():
    total_professionals = Professional.query.count()
    total_customers = Customer.query.count()
    total_service_requests = ServiceRequest.query.count()
    total_services = Service.query.count()
    
    return render_template("admin_summary.html",total_professionals=total_professionals,total_customers=total_customers,total_service_requests=total_service_requests,total_services=total_services)



@app.route("/admin/all_professionals")
@auth_required
def all_professionals():
    professionals = Professional.query.filter_by(verified=True).all()
    return render_template("all_professionals.html",professionals=professionals)


@app.route("/admin/all_customers")
@auth_required
def all_customers():
    customers=Customer.query.all()
    return render_template("all_customers.html",customers=customers)



@app.route("/admin/all_service_requests")
@auth_required
def all_service_requests():
    requests=ServiceRequest.query.all()
    return render_template("service_requests_view.html",requests=requests)




############################### SERVICE #######################################
@app.route("/add/service")
@auth_required
def add_service():
    return render_template("add_service.html")

@app.route("/add/service",methods=["POST"])
@auth_required
def add_service_post():
    name = request.form.get("name")
    description = request.form.get("description")
    base_price = request.form.get("base_price")
    time_required = request.form.get("time_required")
    
    # Validate the required fields
    if not name or not base_price:
        flash("Name and Base Price are required fields.", "danger")
        return redirect(url_for("add_service"))  # Assuming there is a route for displaying the add service form

    if Service.query.filter_by(name=name).first():
        flash("Service by this name already exists.")
        return redirect(url_for("add_service"))
    
    new_service = Service(
            name=name,
            description=description,
            base_price=float(base_price),
            time_required=time_required
        )
        
        
    db.session.add(new_service)
    db.session.commit()
        
    flash("Service added successfully!", "success")
    return redirect(url_for("admin_home"))  



@app.route("/service/<int:service_id>/view")
@auth_required
def view_service(service_id):
    service=Service.query.get(service_id)
    return render_template("service.html",service=service)





@app.route("/service/<int:service_id>/edit")
@auth_required
def edit_service(service_id):
    service=Service.query.get(service_id)
    return render_template("edit_service.html",service=service)

@app.route("/service/<int:service_id>/edit",methods=["POST"])
@auth_required
def edit_service_post(service_id):
    service=Service.query.get(service_id)
    
    new_description=request.form.get("description")
    new_base_price=request.form.get("base_price")
    new_time_required = request.form.get("time_required")
    
    service.description=new_description
    service.base_price=new_base_price
    service.time_required=new_time_required
    
    db.session.commit()
    flash("Service edited successfully!", "success")
    return redirect(url_for("admin_home"))

    
    
@app.route("/service/<int:service_id>/delete",methods=["POST"])
@auth_required
def delete_service(service_id):
    service=Service.query.get(service_id)
    
     
    service_requests = ServiceRequest.query.filter_by(service_id=service_id).all()
    if service_requests:
        flash("Cannot delete service as there are associated service requests.", "warning")
        return redirect(url_for("view_service",service_id=service_id))

    # To delete all service professionals associated with the service
    service_professionals = Professional.query.filter_by(service_type=service.name).all()
    for professional in service_professionals:
        db.session.delete(professional)

    # Delete the service itself
    db.session.delete(service)
    db.session.commit()
    
    flash("Service and associated professionals deleted successfully!", "success")
    return redirect(url_for("admin_home"))
    
    
    
 


    


@app.route("/service/<int:service_id>/<int:customer_id>/service_requests/<int:professional_id>",methods=["GET","POST"])
@auth_required
def service_requests(customer_id,professional_id,service_id):
    customer=Customer.query.get(customer_id)
    professional=Professional.query.get(professional_id)
    service=Service.query.get(service_id)
    
    if request.method == 'GET':
        return render_template("service_requests.html", customer=customer, professional=professional, service=service)



    if request.method == 'POST':
        address = request.form.get('address')
        offered_price=request.form.get("offered_price")
        date_of_request = request.form.get('date_of_request')
        date_of_request = datetime.strptime(date_of_request, '%Y-%m-%d')
        
        
        try:
            offered_price = int(offered_price) if offered_price else service.base_price
        except ValueError:
            flash("Invalid offered price. Please enter a valid number.")
            return render_template("service_requests.html", customer=customer, professional=professional, service=service)
        if offered_price < service.base_price:
            flash("Offered price must be greater than the base price.", "danger")
            return render_template("service_requests.html", customer=customer, professional=professional, service=service)
       
        
        
        
        # Create the service request
        service_request = ServiceRequest(
            service_id=service_id,
            customer_id=customer.customer_id,
            professional_id=professional.prof_id,
            Address=address,
            date_of_request=date_of_request,
            status="requested",
            offered_price=offered_price
        )

        
        db.session.add(service_request)
        db.session.commit()
        flash("Service request created successfully!", "success")
        return redirect(url_for('customer_requests',customer_id=customer_id))  

   

   
@app.route("/delete_service_request/<int:service_req_id>", methods=["POST"])
@auth_required
def delete_service_request(service_req_id):
    service_request = ServiceRequest.query.get(service_req_id)
    if service_request:
        db.session.delete(service_request)
        db.session.commit()
        flash("Service request deleted successfully!", "success")
    else:
        flash("Service request not found.", "danger")
    return redirect(url_for('all_service_requests'))  # Redirect to the list page after deletion



@app.route("/edit_service_request/<int:service_req_id>", methods=["GET","POST"])
@auth_required
def edit_service_request(service_req_id):
    service_request = ServiceRequest.query.get(service_req_id)
    customer_id=service_request.customer_id
    customer=service_request.customer

    
    if request.method=="GET":
        return render_template("edit_sr.html", request=service_request,customer=customer)

    if request.method == "POST":
            # Update the fields with the form data
            service_request.address = request.form.get('address')
            service_request.offered_price = request.form.get('offered_price')
            date_of_request = request.form.get('date_of_request')
            date_of_request = datetime.strptime(date_of_request, '%Y-%m-%d')
            service_request.date_of_request= date_of_request
        

            # Commit the changes to the database
            db.session.commit()

            # Flash success message
            flash("Service request updated successfully!", "success")
            return redirect(url_for('customer_requests',customer_id=customer_id))
      

@app.route('/close_service_request/<int:service_req_id>', methods=['POST'])
@auth_required
def close_service_request(service_req_id):
    service_request = ServiceRequest.query.get(service_req_id)
    customer_id=service_request.customer_id
    if service_request:
        if service_request.status == 'assigned':  # Ensure the request can only be closed if it's still open
            service_request.status = 'closed'
            service_request.date_of_completion = date.today() 
            db.session.commit()
            flash("Service request closed successfully!", "success")
        else:
            flash("Service request cannot be closed as it is already closed.", "danger")
    else:
        flash("Service request not found.", "danger")
    return redirect(url_for('customer_requests',customer_id=customer_id))


@app.route("/review_service_request/<int:service_req_id>", methods=["GET,POST"])
@auth_required
def review_service_request(service_req_id):
    service_request = ServiceRequest.query.get(service_req_id)
    customer_id=service_request.customer_id
    return redirect(url_for('customer_requests',customer_id=customer_id))  





############################# CUSTOMER #####################################







@app.route("/customer/register")
def customer_register():
    return render_template('customer_register.html')

@app.route("/customer/register",methods=["POST"])
def customer_register_post():
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    city = request.form.get("city")
    
    if not username or not password or not email or not city:
        flash("All fields are required.", "error")
        return redirect(url_for("customer_register"))
    
    if Customer.query.filter(Customer.username == username).first():
        flash("Customer with this username already exists. Choose another username.", "error")
        return redirect(url_for("customer_register"))
    
    new_customer = Customer(username=username, password=password, email=email, city=city)
    db.session.add(new_customer)
    db.session.commit()
    flash("Customer successfully registered!")
    
    return redirect(url_for("login"))


@app.route('/block_customer/<int:customer_id>', methods=['POST'])
def block_customer(customer_id):
    customer = Customer.query.get(customer_id)
    customer.block = True
    db.session.commit()
    flash(f"Customer '{customer.username}' has been blocked.", "success")
    
    return redirect(url_for('all_customers'))



@app.route('/unblock_customer/<int:customer_id>', methods=['POST'])
def unblock_customer(customer_id):
    customer = Customer.query.get(customer_id)
    customer.block = False
    db.session.commit()
    flash(f"Customer '{customer.username}' has been unblocked.", "success")
    
    return redirect(url_for('all_customers'))



    

@auth_required
@app.route("/customer/<int:customer_id>/summary")
def customer_history(customer_id):
    customer=Customer.query.get(customer_id)
    requests = ServiceRequest.query.filter(
        ServiceRequest.customer_id == customer_id,
        ServiceRequest.status.in_(["rejected", "closed"])
    ).all()
   
    return render_template("customer_req_history.html",customer=customer,requests=requests)




@auth_required
@app.route("/customer/<int:customer_id>/search",methods=["GET","POST"])
def customer_search(customer_id):
    customer=Customer.query.get(customer_id)
    if request.method=="GET":
        return render_template("customer_search.html",customer=customer)
    
    if request.method=="POST":
        parameter=request.form.get("parameter")
        query=request.form.get("query")
        if not parameter or not query:
            return render_template("customer_search.html",customer=customer)
        else:
            services = Service.query
            if parameter == "service_name":
                services = services.filter(Service.name.ilike(f"%{query}%")).all()
            elif parameter == "base_price":
                try:
                    query_value = float(query)  # Ensure query is a number for price comparison
                    services = services.filter(Service.base_price < query_value).all()
                except ValueError:
                # Handling invalid price format
                    services = []
            elif parameter == "time_required":
                try:
                    query_value = float(query)  # Ensure query is a number for time comparison
                    services = services.filter(Service.time_required > query_value).all()
                except ValueError:

                    services = []
        
        return render_template("customer_search.html", customer=customer,services=services)

    
    
    
    

@auth_required
@app.route("/customer/<int:customer_id>/requests")
def customer_requests(customer_id):
    customer=Customer.query.get(customer_id)
    requests = ServiceRequest.query.filter(
        ServiceRequest.customer_id == customer_id,
        ServiceRequest.status.in_(["requested", "assigned"])
    ).all()
    return render_template("customer_requests.html",customer=customer,requests=requests)



@auth_required
@app.route("/customer/<int:customer_id>/profile")
def customer_profile(customer_id):
    customer=Customer.query.get(customer_id)
    services=Service.query.all()
    if customer.block:
        return render_template("blocked_customer.html",customer=customer)
    return render_template("customer.html",customer=customer,services=services)




@auth_required
@app.route("/customer/<int:customer_id>/service/<int:service_id>")
def customer_service_profs(customer_id,service_id):
    customer=Customer.query.get(customer_id)
    service=Service.query.get(service_id)

    professionals = Professional.query.filter(Professional.verified == True,
                    Professional.service_type == service.name).all()

    
    return render_template("customer_service.html",service=service,customer=customer,professionals=professionals)





############################### PROFESSIONAL #######################################


@app.route('/register_professional', methods=['GET', 'POST'])
def professional_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        service_type = request.form['service_type']
        experience = request.form['experience']
        bio = request.form['bio']
        city = request.form['city']
        file = request.files['verification_document']
        
        if not all([username, password, email, file, service_type]):
            flash("All fields are required.", "error")
            return redirect(url_for("professional_register"))
        
        if Customer.query.filter(Professional.email == email).first():
            flash("This email id has already been registered.", "error")
            return redirect(url_for("professional_register"))
        
       
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # Secure the filename
            file_path = os.path.join("/Users/maitry/Desktop/MAD1/code/uploads", filename)  # Define the file path
            file.save(file_path)

            verification_document_path = file_path
        else:
            flash("Upload the verification dociment in required format only.", "error")
            return redirect(url_for("professional_register"))


        # Creating a new Professional 
        new_professional = Professional(
            username=username,
            password=password,  
            email=email,
            service_type=service_type,
            experience=experience,
            bio=bio,
            city=city,
            verification_document=verification_document_path
        )
        db.session.add(new_professional)
        db.session.commit()
        
        return redirect(url_for("login"))  # Redirect after registration

    # GET request
    services = Service.query.all()
    return render_template('professional_register.html', services=services)




@app.route('/block_prof/<int:prof_id>', methods=['POST'])
def block_prof(prof_id):
    prof = Professional.query.get(prof_id)
    prof.block = True
    db.session.commit()
    flash(f"Professional '{prof.username}' has been blocked.", "success")
    
    return redirect(url_for('all_professionals'))




@app.route('/unblock_prof/<int:prof_id>', methods=['POST'])
def unblock_prof(prof_id):
    prof = Professional.query.get(prof_id)
    prof.block = False
    db.session.commit()
    flash(f"Professional '{prof.username}' has been unblocked.", "success")
    
    return redirect(url_for('all_professionals'))






@auth_required
@app.route("/professional/<int:professional_id>/profile")
def professional_profile(professional_id):
    professional=Professional.query.get(professional_id)
    if professional.verified is None:
        return render_template("prof1.html",professional=professional)
    elif professional.verified is False:
        return render_template("prof2.html",professional=professional)
    elif professional.block:
        return render_template("blocked_prof.html",professional=professional)
    else:
        request1 = ServiceRequest.query.filter(
        ServiceRequest.professional_id == professional_id,
        ServiceRequest.status.in_(["requested", "assigned"])).all()
        
        request2 = ServiceRequest.query.filter(
        ServiceRequest.professional_id == professional_id,
        ServiceRequest.status=="closed").all()
        return render_template("prof_profile.html",professional=professional,request1=request1,request2=request2)
        
    



@auth_required
@app.route("/professional/<int:professional_id>/approve",methods=["POST"])
def approve_professional(professional_id):
    professional=Professional.query.get(professional_id)
    professional.verified=True
    
    db.session.commit()
    flash("Professional verified and approved!", "success")
    return redirect(url_for("admin_requests"))



@auth_required
@app.route("/professional/<int:professional_id>/reject",methods=["POST"])
def reject_professional(professional_id):
    professional=Professional.query.get(professional_id)
    professional.verified=False
    
    db.session.commit()
    flash("Professional rejected!", "success")
    return redirect(url_for("admin_requests"))
    
    
     
@app.route('/accept_service_request/<int:service_req_id>', methods=['POST'])
@auth_required
def accept_service_request(service_req_id):
    service_request = ServiceRequest.query.get(service_req_id)
    professional=service_request.professional
    service_request.status = 'assigned'
    db.session.commit()
    flash('Service request accepted successfully!', 'success')

    return redirect(url_for('professional_profile',professional_id=professional.prof_id))


@app.route('/reject_service_request/<int:service_req_id>', methods=['POST'])
@auth_required
def reject_service_request(service_req_id):
    service_request = ServiceRequest.query.get(service_req_id)
    professional=service_request.professional
    service_request.status = 'rejected'
    db.session.commit()
    flash('Service request rejected!')

    return redirect(url_for('professional_profile',professional_id=professional.prof_id))



@app.route('/close_sr_prof/<int:service_req_id>', methods=['POST'])
@auth_required
def close_sr_prof(service_req_id):
    service_request = ServiceRequest.query.get(service_req_id)
    professional=service_request.professional
    service_request.status = 'closed'
    db.session.commit()
    flash('Service request closed!')

    return redirect(url_for('professional_profile',professional_id=professional.prof_id))


@app.route('/rate_service_request/<int:service_req_id>/<int:customer_id>', methods=['POST'])
@auth_required
def rate_sr(service_req_id,customer_id):
    customer=Customer.query.get(customer_id)
    service_request = ServiceRequest.query.get(service_req_id)
    requests = ServiceRequest.query.filter(
        ServiceRequest.customer_id == customer_id,
        ServiceRequest.status.in_(["rejected", "closed"])
    ).all()
    if service_request.status =='closed':
        service_request.rating=request.form.get('rating')
        
    db.session.commit()
    flash('Service rated successfully!', 'success')

    return redirect(url_for('customer_history',customer_id=customer.customer_id,requests=requests))

