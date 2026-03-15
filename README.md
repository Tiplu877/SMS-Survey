# SMS Survey Manager

SMS Survey Manager is a **Python-based customer feedback system** that allows businesses to manage customer phone numbers and send automated SMS surveys. The system collects ratings from customers and directs satisfied customers to leave a public review while allowing dissatisfied customers to provide private feedback.

The project consists of two main components:

1. **Desktop Management App (Tkinter GUI)** – Used to manage customer phone numbers and send surveys.
2. **Flask SMS Server** – Handles incoming SMS responses and processes feedback using Twilio.

---

# Features

### Customer Management

* Add customer phone numbers
* Remove phone numbers
* View all stored numbers
* Import phone numbers from CSV
* Export phone numbers to CSV

### SMS Survey System

* Send SMS surveys to all stored numbers
* Customers reply with a rating **1–5**
* Automatically handles responses

### Smart Feedback Routing

* **Ratings 4–5:** Customer receives a link to leave a public review
* **Ratings 1–3:** Customer is asked for private feedback

### Feedback Collection

* Stores negative feedback locally
* Sends feedback to company email

### Logging System

* Application logs stored in `app_logs.txt`
* GUI interface to view logs

### Server Integration

* Launch Flask survey server from the GUI
* Twilio handles SMS delivery and response processing

---

# Technologies Used

* **Python**
* **Tkinter** – Desktop GUI
* **Flask** – Web server for handling SMS responses
* **SQLite** – Local database
* **Twilio API** – SMS messaging
* **SMTP (smtplib)** – Email notifications
* **CSV module** – Import/export data
* **PyInstaller** – Packaging the application

---

# Project Structure

```
SMS-Survey-Manager
│
├── main_app.py          # Tkinter desktop application
├── app.py               # Flask server for SMS handling
├── customers.db         # SQLite database
├── app_logs.txt         # Application logs
├── bad_feedback.txt     # Stored negative feedback
└── README.md
```

---

# How It Works

### Step 1 – Add Customer Numbers

Users add phone numbers manually or import them from a CSV file.

### Step 2 – Send Survey

The application sends customers an SMS message asking them to rate their experience.

Example message:

```
How would you rate your experience at COMPANY NAME out of 5?
```

### Step 3 – Customer Replies

Customers reply with a number from **1 to 5**.

### Step 4 – System Response

* **4–5:** Customer receives a review link
* **1–3:** Customer is asked for feedback

### Step 5 – Data Handling

* Numbers are removed after a survey is sent or replied to
* Negative feedback is stored locally

---

# Installation

### 1. Install Python

Download Python from
https://python.org

### 2. Install dependencies

```
pip install flask twilio
```

---

# Environment Variables

Before running the program, set the following environment variables:

```
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE=your_twilio_phone_number
EMAIL_USER=your_email
EMAIL_PASS=your_email_app_password
```

---

# Running the Application

### Start the Flask Server

```
python app.py
```

Server runs on:

```
http://localhost:5000
```

### Run the Desktop Application

```
python main_app.py
```

The GUI allows you to manage numbers and send surveys.

---

# Example Workflow

1. Start the Flask server
2. Open the GUI
3. Import or add customer numbers
4. Click **Send Survey**
5. Customers respond with ratings
6. Feedback is processed automatically

---

# Future Improvements

Possible upgrades for this project:

* Dashboard analytics for ratings
* Web-based admin panel
* AI feedback analysis
* Cloud database support
* Bulk campaign scheduling
* Automatic review tracking

---

# Author

Developed as a **computer science project demonstrating GUI development, API integration, and backend server design using Python**.
