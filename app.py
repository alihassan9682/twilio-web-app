from flask import Flask, request, render_template
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv
from datetime import datetime
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_API_KEY = os.getenv("TWILIO_API_KEY")
TWILIO_API_SECRET = os.getenv("TWILIO_API_SECRET")
TWILIO_APP_SID = os.getenv("TWILIO_APP_SID")
TWILIO_CALLER_ID = os.getenv("TWILIO_CALLER_ID")

client = Client(TWILIO_API_KEY, TWILIO_API_SECRET, TWILIO_ACCOUNT_SID)

@app.context_processor
def inject_now():
    return {'now': datetime.now}

@app.route("/", methods=["GET", "POST"])
def index():
    message = None

    if request.method == "POST":
        action = request.form.get("action")
        to_number = request.form.get("to")

        if action == "call":
            try:
                call = client.calls.create(
                    to=to_number,
                    from_=TWILIO_CALLER_ID,
                    application_sid=TWILIO_APP_SID
                )
                message = f"✅ Call initiated. SID: {call.sid}"
            except Exception as e:
                message = f"❌ Error: {str(e)}"
        elif action == "hangup":
            try:
                # Optional: If you want to hang up active calls programmatically,
                # you must store the call SID and end it here.
                message = "🔴 Hang up requested. (Manual disconnect in demo)"
            except Exception as e:
                message = f"❌ Error hanging up: {str(e)}"

    return render_template("home.html", message=message)


@app.route("/voice", methods=["POST"])
def voice():
    """Optional fallback if App SID doesn't have TwiML configured."""
    response = VoiceResponse()
    response.say("Hello! This is a test call from your Flask app.", voice="alice")
    return str(response)


if __name__ == "__main__":
    app.run(debug=True)
