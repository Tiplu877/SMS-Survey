from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3, re, os

#Twilio Settings
ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "PASTE_YOUR_TWILIO_SID")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "PASTE_YOURTWILIO_TOKEN")
TWILIO_PHONE = os.environ.get("TWILIO_PHONE", "PASTE_YOUR_TWILIO_PHONE") 
REVIEW_LINK = "https://example.com/feedback"

client = Client(ACCOUNT_SID, AUTH_TOKEN)
app = Flask(__name__)

#Database setup
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "customers.db")
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    phone TEXT NOT NULL
)
""")
conn.commit()

#Send survey
def send_survey_sms():
    cursor.execute("SELECT id, phone FROM customers")
    rows = cursor.fetchall()

    for cid, phone in rows:
        digits = re.sub(r"\D", "", phone)
        if len(digits) == 10:
            to_number = "+1" + digits
        elif len(digits) == 11 and digits.startswith("1"):
            to_number = "+" + digits
        else:
            print(f"Skipping invalid number: {phone}")
            continue

        try:
            client.messages.create(
                body="How would you rate your experience at COMPANY NAME out of 5?",
                from_=TWILIO_PHONE,
                to=to_number
            )
            print(f"Sent survey to {to_number}")
        except Exception as e:
            print(f"Failed to send to {to_number}: {e}")
        else:
            cursor.execute("DELETE FROM customers WHERE id=?", (cid,))
            conn.commit()
            print(f"Removed {to_number} from database")



#SMS Reply Handler
@app.route("/sms", methods=["POST"])
def sms_reply():
    body = request.form.get("Body", "").strip()
    from_number = request.form.get("From")
    resp = MessagingResponse()

    digits = re.sub(r"\D", "", from_number)[-10:]
    print(f"[INFO] Received SMS from {from_number}: {body}")

    if body.isdigit() and 1 <= int(body) <= 5:
        rating = int(body)
        if rating >= 4:
            resp.message(f"Thanks for your great rating! \nPlease leave a review: {REVIEW_LINK}")
        else:
            resp.message("Thanks for your honesty \nWhat could we have done better?")
            # Optional: save bad feedback to a file
            with open("bad_feedback.txt", "a") as f:
                f.write(f"{from_number}: {body}\n")
        # Delete number after reply
        cursor.execute("DELETE FROM customers WHERE phone LIKE ?", (f"%{digits}",))
        conn.commit()
        print(f"[INFO] Removed {from_number} after reply")
    else:
        resp.message("Please reply with a number from 1 to 5.")

    return str(resp)

if __name__ == "__main__":
    print("[INFO] Flask server starting on port 5000...")
    app.run(host="0.0.0.0", port=5000)
