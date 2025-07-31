from flask import Flask, request, render_template
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv
from datetime import datetime
import os

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_API_KEY = os.getenv("TWILIO_API_KEY")
TWILIO_API_SECRET = os.getenv("TWILIO_API_SECRET")
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
                # Use your public URL exposed via ngrok/devtunnel
                twiml_url = "https://j563v1vz-5050.inc1.devtunnels.ms/voice"

                call = client.calls.create(
                    to=to_number,
                    from_=TWILIO_CALLER_ID,
                    url=twiml_url,
                    method="POST"
                )
                message = f"✅ Call initiated. SID: {call.sid}"
            except Exception as e:
                message = f"❌ Error: {str(e)}"

        elif action == "hangup":
            message = "🔴 Hang up requested. (Manual disconnect in demo)"

    return render_template("home.html", message=message)


@app.route("/voice", methods=["GET", "POST"])
def voice():
    response = VoiceResponse()

    # Add a pause of 10 seconds before any speech
    response.pause(length=10)

    # Gather input after pause
    gather = response.gather(
        num_digits=1,
        action=request.url_root.rstrip("/") + "/gather",
        method="POST"
    )
    gather.say("Hello! This is Lingopal Web Caller. Press 1 for sales. Press 2 for support.", voice="alice")

    # Say goodbye if no input is received
    response.say("We didn't receive any input. Goodbye!", voice="alice")

    return str(response)


@app.route("/gather", methods=["GET", "POST"])
def gather():
    digit = request.form.get("Digits")
    response = VoiceResponse()

    if digit == "1":
        response.say("You selected Sales. Please wait while we connect you.", voice="alice")
    elif digit == "2":
        response.say("You selected Support. We will assist you shortly.", voice="alice")
    else:
        response.say("Invalid input. Goodbye!", voice="alice")

    return str(response)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
