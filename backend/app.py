from flask import Flask, request, jsonify
from flask_cors import CORS
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import requests
from dotenv import load_dotenv
import os

load_dotenv() 

app = Flask(__name__)
CORS(app)
def get_basic_phone_info(phonenumber):
    number = phonenumbers.parse(phonenumber)
    country = geocoder.description_for_number(number, 'en')
    service_provider = carrier.name_for_number(number, 'en')
    timezones = timezone.time_zones_for_number(number)
    return country, service_provider, timezones

def get_numverify_info(phonenumber):
    api_key = os.getenv('NUMVERIFY_API_KEY')
    url = f"http://apilayer.net/api/validate?access_key={api_key}&number={phonenumber}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def get_twilio_info(phonenumber):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    lookup_url = f"https://lookups.twilio.com/v1/PhoneNumbers/{phonenumber}"
    response = requests.get(lookup_url, auth=(account_sid, auth_token))
    return response.json() if response.status_code == 200 else None

def get_numlookupapi_info(phonenumber):
    api_key = os.getenv('NUMLOOKUPAPI_KEY')
    url = f"https://www.numlookupapi.com/api/v1/validate/{phonenumber}?apikey={api_key}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def get_ipqualityscore_info(phonenumber):
    api_key = os.getenv('IPQUALITYSCORE_API_KEY')
    url = f"https://ipqualityscore.com/api/json/phone/{api_key}/{phonenumber}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def extract_info(response):
    relevant_info = {}
    other_info = {}
    
    if response:
        if "phone_number" in response:
            relevant_info["Phone Number"] = response.get("phone_number")
        if "valid" in response:
            relevant_info["Validity"] = "Yes" if response.get("valid") else "No"
        if "country_code" in response:
            relevant_info["Country Code"] = response.get("country_code")
        if "location" in response:
            relevant_info["Location"] = response.get("location")
        if "carrier" in response:
            relevant_info["Carrier"] = response.get("carrier")
        if "line_type" in response:
            relevant_info["Line Type"] = response.get("line_type")
        if "fraud_score" in response:
            relevant_info["Fraud Score"] = response.get("fraud_score")
        if "recent_abuse" in response:
            relevant_info["Recent Abuse"] = response.get("recent_abuse")

        other_info = {key: value for key, value in response.items() if key not in relevant_info}

    return relevant_info, other_info

def phone_number_osint(phonenumber):
    combined_relevant_info = {}
    combined_other_info = {}
    tool_count = 0

    country, service_provider, timezones = get_basic_phone_info(phonenumber)
    combined_relevant_info.update({
        "Phone Number": phonenumber,
        "Country": country,
        "Carrier": service_provider,
        "Timezones": ", ".join(timezones)
    })
    tool_count += 1

    numverify_info = get_numverify_info(phonenumber)
    if numverify_info:
        relevant, other = extract_info(numverify_info)
        combined_relevant_info.update(relevant)
        combined_other_info.update(other)
        tool_count += 1

    twilio_info = get_twilio_info(phonenumber)
    if twilio_info:
        relevant, other = extract_info(twilio_info)
        combined_relevant_info.update(relevant)
        combined_other_info.update(other)
        tool_count += 1

    numlookupapi_info = get_numlookupapi_info(phonenumber)
    if numlookupapi_info:
        relevant, other = extract_info(numlookupapi_info)
        combined_relevant_info.update(relevant)
        combined_other_info.update(other)
        tool_count += 1

    ipqualityscore_info = get_ipqualityscore_info(phonenumber)
    if ipqualityscore_info:
        relevant, other = extract_info(ipqualityscore_info)
        combined_relevant_info.update(relevant)
        combined_other_info.update(other)
        tool_count += 1

    return combined_relevant_info, combined_other_info, tool_count

@app.route('/process', methods=['POST'])
def process_input():
    data = request.json
    user_input = data.get('input')

    relevant_info, other_info, tool_count = phone_number_osint(user_input)
    
    output = {
        "relevant_info": relevant_info,
        "other_info": other_info,
        "tool_count": tool_count
    }

    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)
