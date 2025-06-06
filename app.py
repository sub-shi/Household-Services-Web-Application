from flask import Flask, render_template, request, send_from_directory, url_for, redirect, flash, Blueprint, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime, timezone
from datetime import date
from werkzeug.utils import secure_filename
import os
import plotly.graph_objs as go
import json
import plotly

#INTIALISING APPS 

app = Flask(__name__) 
import config

import models
from models import *                               # IMPORTING EVERYTHING FROM MODELS

##BASE

@app.route("/")
def home():
    return render_template("home.html")


#UPLOAD FILES PATH

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(app.root_path, 'static', 'uploads'), filename)


#REGISTRATION PAGE

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users=User.query.all()                                    # FETCHING THE USER FROM THE DATABASE
        professionals=service_professionals.query.all()           # FETCHING THE PROFESSIONALS FROM THE DATABASE
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        cpassword=request.form.get('cpassword')
        role = request.form.get('role')
        service_type = request.form.get('service_type') if role == 'service_pro' else None
        experience = request.form.get('experience') if role == 'service_pro' else None

        # CHECKING IF USERNAME ALREADY EXISTS

        for user in users:
              if(user.username==username):
                     return render_template('register.html',message='Username already exsistS!')
              
        for professional in professionals:
              if professional.username == username:
                     return render_template('register.html', message='Username already exists!')
        
        # CREATING A NEW USER

        if cpassword != password:
            return render_template('register.html')
        
        # FOR CUSTOMERS
        if role == 'customer':
            new_user = User(name=name, username=username, role='customer', password_hash=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()

            return redirect('/userlogin')
        
        #FOR SERVICE PROFESSIONALS
        elif role == 'service_pro':
            if not service_type or not experience:
                return render_template('register.html')
            
            new_professional = service_professionals(name=name, username=username, password_hash=generate_password_hash(password), service_type=service_type, experience=experience)
            db.session.add(new_professional)
            db.session.commit()

            return redirect('/userlogin') 

    return render_template('register.html')


#USER LOGIN PAGE

@app.route("/userlogin", methods=['GET', 'POST'])
def userlog():
    if request.method == "GET":
        return render_template('userlogin.html')

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        # Fetch user and professional
        user = User.query.filter_by(username=username).first()
        professional = service_professionals.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password_hash, password):
                print("Customer login successful.")
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                return redirect('/customer_dashboard')
            else:
                return "Invalid customer password"

        elif professional:
            if check_password_hash(professional.password_hash, password):
                print("Professional login successful.")
                session['user_id'] = professional.id
                session['username'] = professional.username
                session['role'] = 'service_pro'
                return redirect('/pro_dashboard')
            else:
                return "Invalid professional password"

        else:
            return "Invalid username"


            
#CREATING ADMIN IF IT DOESN'T EXIST
            
admin = User.query.filter_by(is_admin=True).first()
if not admin:
       admin = User(username='kashi', password='admin', name='kashi', role='admin', is_admin=True)
       db.session.add(admin)
       db.session.commit()
            
#ADMIN LOGIN PAGE

@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlog():
    if request.method == "GET":
        return render_template('adminlogin.html')

    if request.method == "POST":
        admin_id = request.form.get('admin_id')
        password = request.form.get('password')

        user = User.query.filter_by(username=admin_id, role='admin').first()

        if not user:
            return render_template('adminlogin.html', message="Admin not found!")

        if not user.check_password_correction(attempted_password=password):
            return render_template('adminlogin.html', message="Invalid password!")

        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role

        return redirect('/admin_dashboard')

#ADMIN DASHBOARD

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('user_id') or session.get('role') != 'admin':
        return redirect('/adminlogin')


    service_requests_list = service_requests.query.all()


    pending_count = len([req for req in service_requests_list if req.service_status.lower() == 'pending'])
    rejected_count = len([req for req in service_requests_list if req.service_status.lower() == 'rejected'])
    completed_count = len([req for req in service_requests_list if req.service_status.lower() == 'completed'])


    labels = ['pending', 'Rejected', 'completed']
    counts = [pending_count, rejected_count, completed_count]
    colors = ['#f0ad4e', '#d9534f', '#5cb85c']


    fig = go.Figure(data=[
        go.Pie(labels=labels, values=counts, marker=dict(colors=colors), hole=0.3)
    ])
    fig.update_layout(title='Overall Service Request Status')


    graph_html = fig.to_html(full_html=False)

    return render_template('admin_dashboard.html', username=session.get('username'), graph_html=graph_html, service_requests=service_requests_list)



#CUSTOMER DASHBOARD

@app.route('/customer_dashboard', methods=['GET', 'POST'])
def customer_dashboard():

    if not session.get('user_id') or session.get('role') != 'customer':
        return redirect('/userlogin')

    customer_id = session['user_id'] 


    if request.method == 'POST':
        search_query = request.form.get('query', '').strip()
        pincode = request.form.get('pincode', '').strip()

        query = services.query
        if search_query:
            query = query.filter(services.name.ilike(f"%{search_query}%"))
        if pincode:
            query = query.filter(services.pincode == pincode)

        filtered_services = query.all()
    else:
        filtered_services = services.query.all()

    # FETCHING SERVICE REQUEST COUNTS GROUPED BY STATUS FOR THE GRAPH

    statuses = db.session.query(service_requests.service_status, db.func.count(service_requests.id)).filter_by(customer_id=customer_id).group_by(service_requests.service_status).all()

    # PREPARING DATA FOR THE GRAPH
    
    labels = ["pending", "Rejected", "completed"]
    counts = {status: 0 for status in labels} 

    for status, count in statuses:
        if status in counts:                # CHECKING TO ENSURE THE STATUS IS IN THE LABELS LIST
            counts[status] = count

    values = [counts["pending"], counts["Rejected"], counts["completed"]]

    # CREATING A BAR CHART USING HTML STRING

    bar_chart = go.Figure(data=[
        go.Bar(
            x=labels, y=values, marker=dict(color=['#00FFFF', '#E60000', '#FFBF00']), text=values, textposition='auto')])

    # UPDATING CHART LAYOUT
    
    bar_chart.update_layout(
        title="Service Requests Overview",
        xaxis_title="Status",
        yaxis_title="Number of Requests",
        template="plotly_white",  # Clean theme
        margin=dict(t=50, b=50, l=50, r=50)
    )

    # GENERATING THE CHART AS AN HTML DIV
    chart_html = bar_chart.to_html(full_html=False)


    return render_template('customer_dashboard.html', services=filtered_services, username=session.get('username'), chart_html=chart_html)


# CUSTOMER PROFILE PAGE

@app.route('/customer_profile', methods=['GET', 'POST'])
def customer_profile():
    if not session.get('user_id') or session.get('role') != 'customer':
        return redirect('/userlogin') 

    customer = User.query.get(session.get('user_id'))

    if not customer:
        return "Customer not found"

    if request.method == 'POST':
        new_address = request.form.get('address', '').strip()
        if new_address:
            customer.address = new_address
            db.session.commit()
            message = "Address updated successfully."
        else:
            message = "Address cannot be empty."

        return render_template('customer_profile.html', customer=customer, message=message)

    return render_template('customer_profile.html', customer=customer)

#SEARCH SERVICES [FOR CUSTOMERS]

@app.route('/search_services', methods=['POST'])
def search_services():
    search_query = request.form.get('query', '').strip()                   # GETTING THE SEARCH QUERY FROM THE FORM

    if not search_query:                                                     #IF SEARCH QUERY IS EMPTY
        return render_template('customer_dashboard', message="Please fill out the form")

    all_services = services.query.filter(services.name.ilike(f"%{search_query}%")).all()                                                            # FETCHING PROFESSIONALS USING CASE-INSENSITIVE MATCHING

    if not all_services:
        return render_template('customer_dashboard.html', services=[], message="No professionals found matching your query.")


    return render_template('search_services.html', services=all_services)

#BOOK SERVICE [FOR CUSTOMERS]

@app.route('/book_service/<int:service_id>', methods=['POST'])
def book_service(service_id):
    if not session.get('user_id') or session.get('role') != 'customer':
        return redirect('/userlogin')

    service = services.query.get(service_id)
    if not service:
        return "Service not found"

    new_booking = service_requests(service_id=service.id,customer_id=session['user_id'],service_status="pending",remarks=request.form.get('remarks', ''))
    db.session.add(new_booking)
    db.session.commit()

    return redirect('/manage_service_requests')

#MANAGE SERVICE REQUESTS [FOR CUSTOMERS]

@app.route('/manage_service_requests', methods=['GET'])
def manage_service_requests():
    if not session.get('user_id') or session.get('role') != 'customer':
        return redirect('/userlogin')

    # FETCHING ONLY THE SERVICE REQUESTS THAT ARE NOT CLOSED FOR THE LOGGING IN CUSTOMER
    customer_id = session['user_id']
    bookings = service_requests.query.filter_by(customer_id=customer_id).filter(service_requests.service_status.in_(['pending', 'closed'])).all()

    return render_template('manage_service_requests.html', bookings=bookings)

#DELETE SERVICE REQUEST [FOR CUSTOMERS]

@app.route('/delete_service_request/<int:request_id>', methods=['POST'])
def delete_service_request(request_id):
    if not session.get('user_id'):
        return redirect('/userlogin') 

    service_request = service_requests.query.get(request_id)
    
    if not service_request or service_request.customer_id != session.get('user_id'):
        return "Access Denied or Service Request not found"

    db.session.delete(service_request)
    db.session.commit()

    return redirect('/manage_service_requests')

#UPDATE SERVICE REQUEST [FOR CUSTOMERS]

@app.route('/update_service_request/<int:request_id>', methods=['POST'])
def update_service_request(request_id):
    if not session.get('user_id'):
        return redirect('/userlogin') 

    service_request = service_requests.query.get(request_id)

    if not service_request or service_request.customer_id != session.get('user_id'):
        return "Service Request not found"

    updated_remarks = request.form.get('remarks', '').strip()

    service_request.remarks = updated_remarks
    db.session.commit()

    return redirect('/manage_service_requests')

#CLOSE SERVICE REQUEST [FOR CUSTOMERS]

@app.route('/close_service_request/<int:request_id>', methods=['POST'])
def close_service_request(request_id):
    if not session.get('user_id') or session.get('role') != 'customer':
        return redirect('/userlogin') 

    service_request = service_requests.query.filter_by(id=request_id, customer_id=session.get('user_id')).first()

    if not service_request:
        return "Service request not found."

    service_request.service_status = 'closed'

    db.session.commit()

    return redirect('/manage_service_requests')

#REOPEN SERVICE REQUEST [FOR CUSTOMERS]

@app.route('/reopen_service_request/<int:request_id>', methods=['POST'])
def reopen_service_request(request_id):
    if not session.get('user_id') or session.get('role') != 'customer':
        return redirect('/userlogin')
    
    service_request = service_requests.query.get(request_id)
    
    if service_request and service_request.customer_id == session['user_id'] and service_request.service_status == 'closed':
        service_request.service_status = 'pending'
        
        db.session.commit()
        
        return redirect('/manage_service_requests')
    
    return "Invalid request."

#CUSTOMER BOOKINGS 

@app.route('/customer_bookings', methods=['GET'])
def customer_bookings():
    if not session.get('user_id') or session.get('role') != 'customer':
        return redirect('/userlogin')

    customer_id = session['user_id']

    service_requests_list = service_requests.query.filter(service_requests.customer_id == customer_id,service_requests.service_status.in_(['accepted', 'Rejected', 'completed'])).all()

    return render_template('customer_bookings.html', service_requests=service_requests_list)

#SERVICE PROFESSIONAL DASHBOARD

@app.route('/pro_dashboard', methods=['GET'])
def pro_dashboard():
    if session.get('role') != 'service_pro':
        return redirect('/userlogin')


    professional = service_professionals.query.get(session['user_id'])
    if not professional:
        return "Professional not found."


    service_type = professional.service_type
    service_requests_list = db.session.query(service_requests).join(services).filter(func.lower(services.name) == func.lower(service_type)).all()


    pending_count = len([req for req in service_requests_list if req.service_status.lower() == 'pending'])
    rejected_count = len([req for req in service_requests_list if req.service_status.lower() == 'rejected'])
    completed_count = len([req for req in service_requests_list if req.service_status.lower() == 'completed'])

    labels = ['pending', 'Rejected', 'completed']
    counts = [pending_count, rejected_count, completed_count]
    colors = ['#f0ad4e', '#d9534f', '#5cb85c']


    fig = go.Figure(data=[
        go.Bar(x=labels, y=counts, marker_color=colors)
    ])
    fig.update_layout(title='Service Request Status', xaxis_title='Status', yaxis_title='Count')


    graph_html = fig.to_html(full_html=False)

    return render_template('pro_dashboard.html', service_requests=service_requests_list, graph_html=graph_html)

#ACCEPT SERVICE REQUEST [FOR PROFESSIONALS]

@app.route('/accept_service_request/<int:request_id>', methods=['POST'])
def accept_service_request(request_id):
    if not session.get('user_id') or session.get('role') != 'service_pro':
        return redirect('/userlogin')

    service_request = service_requests.query.get(request_id)

    if not service_request:
        return f"Service request with ID {request_id} not found"

    if service_request.professional_id is not None:
        return "Already assigned to another professional"

    service_request.professional_id = session['user_id']
    service_request.service_status = 'accepted'

    db.session.commit()

    return redirect('/pro_dashboard')

#REJECT SERVICE REQUEST [FOR PROFESSIONALS]

@app.route('/reject_service_request/<int:request_id>', methods=['POST'])
def reject_service_request(request_id):
    if not session.get('user_id') or session.get('role') != 'service_pro':
        return redirect('/userlogin')

    service_request = service_requests.query.get(request_id)

    if not service_request:
        return f"Service request with ID {request_id} not found"

    if service_request.professional_id is not None:
        return "Already assigned to another professional"
    service_request.professional_id = session['user_id'] 

    service_request.service_status = 'Rejected'

    db.session.commit()

    return redirect('/pro_dashboard')

#PROFESSIONALS PROFILE PAGE

@app.route('/profile', methods=['GET', 'POST'])
def professional_profile():
    if not session.get('user_id') or session.get('role') != 'service_pro':
        return redirect('/userlogin')
    
    professional = service_professionals.query.filter_by(id=session['user_id']).first()

    if request.method == 'POST':
        professional.name = request.form.get('name', professional.name)
        professional.description = request.form.get('description', professional.description)
        professional.experience = request.form.get('experience', professional.experience)


        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            filename = secure_filename(file.filename)
            file.save(os.path.join('static', filename)) 
            professional.profile_docs = filename

        db.session.commit()
        return redirect('/profile')

    return render_template('professional_profile.html', professional=professional)

#HISTORY [FOR PROFESSIONALS]

@app.route('/history', methods=['GET', 'POST'])
def history():
    if session.get('role') != 'service_pro':
        return redirect('/userlogin')

    professional = service_professionals.query.get(session['user_id'])
    if not professional:
        return "Professional not found."

    service_requests_list = service_requests.query.filter(service_requests.professional_id == professional.id,service_requests.service_status.in_(['accepted', 'Rejected', 'completed'])).all()

    if request.method == 'POST':
        request_id = request.form.get('request_id')
        service_request = service_requests.query.get(request_id)

        if service_request and service_request.professional_id == professional.id:
            if service_request.service_status == 'accepted': 
                service_request.service_status = 'completed'
                service_request.date_of_completion = datetime.now().date()  
                service_request.remarks = request.form.get('remarks', '')  
                db.session.commit()  

        return redirect('/history') 
    
    return render_template('history.html', service_requests=service_requests_list)

#MANAGE CUSTOMERS [FOR ADMIN]

@app.route('/manage_customers')
def manage_customers():
    customers = User.query.filter_by(role='customer').all()                       #FETCHING THE USER FROM THE DATABASE
    return render_template('manage_customers.html', customers=customers)

#BLOCK A CUSTOMER [FOR ADMIN]

@app.route('/block_customer/<int:user_id>', methods=['POST'])
def block_customer(user_id):
    user = User.query.filter_by(id=user_id).first()                                # FETCHING THE USER FROM THE DATABASE
    if not user:
        return "Customer not found"
    user.status = 'blocked'                                                        # UPDATING THE STATUS TO "BLOCKED"
    db.session.commit()
    return redirect('/manage_customers')

#MANAGE SERVICE PROFESSIONALS [FOR ADMIN]

@app.route('/manage_professionals')
def manage_professionals():
    professionals = service_professionals.query.all()                           # FETCHING THE SERVICE PROFESSIONAL FROM THE DATABASE
    return render_template('manage_professionals.html', professionals=professionals)

#APPROVE A SERVICE PROFESSIONALS [FOR ADMIN]

@app.route('/approve_professional/<int:professional_id>', methods=['POST'])
def approve_professional(professional_id):

    professional = service_professionals.query.get(professional_id)             # FETCHING THE SERVICE PROFESSIONAL FROM THE DATABASE
    if not professional:
        return "Service Professional not found"

    professional.status = 'approved'                                         # UPDATING THE STATUS TO "APPROVED"
    db.session.commit()
    return redirect('/manage_professionals')

#BLOCK A SERVICE PROFESSIONALS [FOR ADMIN]

@app.route('/block_professional/<int:professional_id>', methods=['POST'])
def block_professional(professional_id):

    professional = service_professionals.query.get(professional_id)
    if not professional:
        return "Service Professional not found"

    professional.status = 'blocked'                                          # UPDATING THE STATUS TO "BLOCKED"
    db.session.commit()
    return redirect('/admin_dashboard')

#SEARCH FOR SERVICE PROFESSIONALS USING USERNAME [FOR ADMIN]

@app.route('/search', methods=['POST'])
def search_professional():
    search_query = request.form.get('query', '').strip()                   # GETTING THE SEARCH QUERY FROM THE FORM

    if not search_query:                                                     #IF SEARCH QUERY IS EMPTY
        return render_template('admin_dashboard.html', message="Please fill out the form")

    professionals = service_professionals.query.filter(service_professionals.username.ilike(f"%{search_query}%")).all()                                                            # FETCHING PROFESSIONALS USING CASE-INSENSITIVE MATCHING

    if not professionals:
        return render_template('admin_dashboard.html', professionals=[], message="No professionals found matching your search.")


    return render_template('search_professionals.html', professionals=professionals)

#UNBLOCK AN SERVICE PROFESSIONAL [FOR ADMIN]

@app.route('/unblock_professional/<int:professional_id>', methods=['POST'])
def unblock_professional(professional_id):
    if session.get('role') != 'admin':
        return "Access Denied"

    professional = service_professionals.query.get(professional_id)
    if not professional:
        return "Service Professional not found"

    professional.status = 'approved'                                             # UPDATING THE STATUS TO "APPROVED"
    db.session.commit()
    return redirect('/admin_dashboard')

#CREATE NEW SERVICE FEATURE [FOR ADMIN]

@app.route('/create_service', methods=['GET', 'POST'])
def create_service():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        time_required = request.form.get('time')
        pincode = request.form.get('pincode')
        description = request.form.get('description')

        new_service = services(name=name, price=price, time_required=time_required, pincode=pincode, description=description)
        db.session.add(new_service)
        db.session.commit()
        return redirect('/admin_dashboard')
    
    return render_template('create_service.html')

#MANAGE SERVICES [FOR ADMIN]

@app.route('/manage_services')
def manage_services():
    try:
        services_list = db.session.query(services).all()

        # FETCHING ALL BOOKED SERVICE IDS FROM THE SERVICE REQUESTS TABLE

        booked_service_ids = {request.service_id for request in db.session.query(service_requests.service_id).distinct()}

        for service in services_list:
            service.is_booked = service.id in booked_service_ids

    except Exception as e:
        print(f"Error fetching services: {e}")
        services_list = []                                                # DEFAULT VALUE IN CASE OF AN ERROR

    return render_template('manage_service.html', services=services_list)

#UPDATE EXISTING SERVICES [FOR ADMIN]

@app.route('/update_service/<int:service_id>', methods=['POST'])
def update_service(service_id):
    service = services.query.get(service_id)                             # FETCHING THE SERVICES FROM THE DATABASE

    if service is None:
        flash('Service not found!')
        return redirect('/manage_services')
    
    # UPDATING SERVICE DETAILS

    service.name = request.form.get('name')
    service.price = request.form.get('price')
    service.time_required = request.form.get('time_required')
    db.session.commit()

    return redirect('/manage_services')

#DELETE A SERVICE [FOR ADMIN]

@app.route('/delete_service/<int:service_id>', methods=['POST'])
def delete_service(service_id):
    service = services.query.get(service_id)                                # FETCHING THE SERVICES FROM THE DATABASE

    if service is None:
        return redirect('/manage_services')
    
    db.session.delete(service)
    db.session.commit()

    return redirect('/manage_services')

#BOOKING [FOR ADMIN]

@app.route('/admin_bookings', methods=['GET'])
def admin_bookings():
    if not session.get('user_id') or session.get('role') != 'admin':
        return redirect('/admin_login') 

    service_requests_list = service_requests.query.all()

    return render_template('admin_bookings.html', service_requests=service_requests_list)

#LOGOUT SESSION

@app.route("/logout", methods=["GET", "POST"]) 
def logout():
    if current_user.is_authenticated: 
        total_session_time = 0
        if current_user.login_time: 
            session_duration = round(((datetime.now() - current_user.login_time).seconds) / 60, 2)
            total_session_time += session_duration

            current_user.total_active_hours += (total_session_time / 60)
            current_user.login_time = None
            db.session.commit() 

    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)

