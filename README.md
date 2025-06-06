
# Household Services Web Application

A full-stack **Household Services Web Application** built with **Flask**, inspired by platforms like **Urban Company**. The application allows users to seamlessly book household services such as **AC repair**, **plumbing**, **electrical work**, and more.

**Service professionals** can manage service requests, while an **admin dashboard** provides tools for user and service management. The project demonstrates advanced concepts in **web development**, **database management**, and **data visualization**.

## Features

- Service Discovery — Customers can browse and book a wide range of household services.
- Service Professionals Management — Each professional has a specific role and pricing.
- Booking Management — Professionals can accept and manage service requests.
- Role-Based Access Control — Separate roles for **Admin**, **Service Professionals**, and **Customers**.
- Analytics Dashboard — Visualize service trends and activity using **Matplotlib**.
- Reviews and Ratings — Users can leave feedback for completed services.
- Authentication & Authorization — Secure login and role-based features.
- Responsive UI — Built with **Bootstrap** for a modern user experience.

## Tech Stack

**Backend:**

- Python
- Flask
- SQLite + SQLAlchemy ORM

**Frontend:**

- HTML5 / CSS3
- Bootstrap
- JavaScript
- Jinja2 Templating Engine

**Additional Libraries:**

- Matplotlib (Data Visualization)

## Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/sub-shi/Household-Services-Web-Application
cd household-services-web-app
```

### 2️⃣ Create a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
# Activate virtual environment:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Application

```bash
python app.py
```

### 5️⃣ Access the App

Open your browser and navigate to:

```
http://localhost:5000
```

## Project Structure (Example)

```
household-services-web-app/
│
├── static/                   # Static files (CSS, JS, Images)
├── templates/                # HTML templates (Jinja2)
├── app.py                    # Main Flask application
├── models.py                 # Database models (SQLAlchemy)
├── requirements.txt          # Project dependencies
├── README.md                 # Project documentation
├── .gitignore                # Files & folders to ignore in git
└── other modules & files
```

## Possible Improvements (Future Scope)

- Integration of a payment gateway (Razorpay/Stripe/PayPal)
- Real-time notifications (email/SMS)
- In-app chat between customers and professionals
- Enhanced service filtering and search functionality
- Mobile app (React Native/Flutter) version
- Multi-language support
- Advanced admin analytics dashboard

## License

This project is licensed for educational and demonstration purposes.
Feel free to fork it, improve it, and use it in your own portfolio projects.
Attribution is appreciated!
