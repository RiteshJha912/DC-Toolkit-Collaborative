from flask import Flask, request, jsonify
from flask_cors import CORS
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import requests
import instaloader
import tweepy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_basic_phone_info(phonenumber):
    try:
        number = phonenumbers.parse(phonenumber)
        country = geocoder.description_for_number(number, 'en')
        service_provider = carrier.name_for_number(number, 'en')
        timezones = timezone.time_zones_for_number(number)
        return {
            "Country": country,
            "Service Provider": service_provider,
            "Timezones": ", ".join(timezones)
        }
    except phonenumbers.phonenumberutil.NumberParseException:
        return {"Error": "Invalid phone number."}

def get_numverify_info(phonenumber):
    api_key = os.getenv('NUMVERIFY_API_KEY')
    url = f"http://apilayer.net/api/validate?access_key={api_key}&number={phonenumber}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {"Error": "Failed to fetch NumVerify info."}

def get_twilio_info(phonenumber):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    lookup_url = f"https://lookups.twilio.com/v1/PhoneNumbers/{phonenumber}"
    response = requests.get(lookup_url, auth=(account_sid, auth_token))
    return response.json() if response.status_code == 200 else {"Error": "Failed to fetch Twilio info."}

def get_numlookupapi_info(phonenumber):
    api_key = os.getenv('NUMLOOKUPAPI_KEY')
    url = f"https://www.numlookupapi.com/api/v1/validate/{phonenumber}?apikey={api_key}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {"Error": "Failed to fetch NumLookup API info."}

def get_ipqualityscore_info(phonenumber):
    api_key = os.getenv('IPQUALITYSCORE_API_KEY')
    url = f"https://ipqualityscore.com/api/json/phone/{api_key}/{phonenumber}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {"Error": "Failed to fetch IPQualityScore info."}

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

def get_instagram_info(username):
    x = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(x.context, username)
        return {
            "Username": profile.username,
            "ID": profile.userid,
            "Full Name": profile.full_name,
            "Biography": profile.biography,
            "Business Category": profile.business_category_name,
            "External URL": profile.external_url,
            "Followers": profile.followers,
            "Following": profile.followees,
            "Media Count": profile.mediacount,
            "Is Private": profile.is_private,
            "Is Verified": profile.is_verified,
            "Profile Picture URL": profile.profile_pic_url
        }
    except instaloader.exceptions.InstaloaderException as e:
        return {"Error": str(e)}

def get_twitter_info(username):
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    client = tweepy.Client(bearer_token=bearer_token)
    try:
        user = client.get_user(username=username, user_fields=["id", "name", "username", "location", "description", "public_metrics", "verified", "created_at"])
        if user.data:
            user_data = user.data
            return {
                "Name": user_data['name'],
                "Username": user_data['username'],
                "User ID": user_data['id'],
                "Description": user_data['description'],
                "Location": user_data['location'],
                "Followers Count": user_data['public_metrics']['followers_count'],
                "Following Count": user_data['public_metrics']['following_count'],
                "Tweet Count": user_data['public_metrics']['tweet_count'],
                "Account Created At": user_data['created_at'],
                "Verified": user_data['verified']
            }
        else:
            return {"Error": "User not found on Twitter."}
    except tweepy.TweepyException as e:
        return {"Error": str(e)}

def get_github_info(username):
    url = f"https://api.github.com/users/{username}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            user_data = response.json()
            return {
                "Username": user_data['login'],
                "ID": user_data['id'],
                "Full Name": user_data.get('name', 'N/A'),
                "Bio": user_data.get('bio', 'N/A'),
                "Public Repos": user_data['public_repos'],
                "Followers": user_data['followers'],
                "Following": user_data['following'],
                "Profile Created At": user_data['created_at'],
                "Profile URL": user_data['html_url']
            }
        else:
            return {"Error": f"User {username} not found on GitHub."}
    except requests.exceptions.RequestException as e:
        return {"Error": str(e)}

def phone_number_osint(phonenumber):
    combined_relevant_info = {}
    combined_other_info = {}

    basic_info = get_basic_phone_info(phonenumber)
    combined_relevant_info.update(basic_info)

    numverify_info = get_numverify_info(phonenumber)
    if numverify_info:
        relevant, other = extract_info(numverify_info)
        combined_relevant_info.update(relevant)
        combined_other_info.update(other)

    twilio_info = get_twilio_info(phonenumber)
    if twilio_info:
        relevant, other = extract_info(twilio_info)
        combined_relevant_info.update(relevant)
        combined_other_info.update(other)

    numlookupapi_info = get_numlookupapi_info(phonenumber)
    if numlookupapi_info:
        relevant, other = extract_info(numlookupapi_info)
        combined_relevant_info.update(relevant)
        combined_other_info.update(other)

    ipqualityscore_info = get_ipqualityscore_info(phonenumber)
    if ipqualityscore_info:
        relevant, other = extract_info(ipqualityscore_info)
        combined_relevant_info.update(relevant)
        combined_other_info.update(other)

    return combined_relevant_info, combined_other_info

def get_hunter_info(email):
    api_key = os.getenv('HUNTER_API_KEY')
    url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={api_key}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {"Error": "Failed to fetch Hunter.io info."}

import re
import dns.resolver

def validate_email_format(email):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email)

def extract_email_domain(email):
    try:
        return email.split('@')[1]
    except IndexError:
        return None

def check_mx_records(domain):
    try:
        records = dns.resolver.resolve(domain, 'MX')
        return [str(record.exchange) for record in records]
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
        return []

def is_disposable_email(domain):
    disposable_domains = [
        "mailinator.com", "10minutemail.com", "guerrillamail.com", "dispostable.com"
    ]
    return domain in disposable_domains

def analyze_email_without_api(email):
    info = {}

    if validate_email_format(email):
        info["Valid Format"] = "Yes"
    else:
        info["Valid Format"] = "No"
        return info

    domain = extract_email_domain(email)
    if domain:
        info["Domain"] = domain
        info["Disposable Email"] = "Yes" if is_disposable_email(domain) else "No"
        mx_records = check_mx_records(domain)
        if mx_records:
            info["MX Records"] = mx_records
        else:
            info["MX Records"] = "None (No email setup detected)"
    else:
        info["Domain"] = "Invalid email structure"

    return info

@app.route('/process', methods=['POST'])
def process_input():
    data = request.json

    phone_number = data.get('phoneNumber')
    instagram_username = data.get('instagramUsername')
    twitter_username = data.get('twitterUsername')
    github_username = data.get('githubUsername')
    email = data.get('email')

    results = {}

    if phone_number:
        phone_relevant_info, phone_other_info = phone_number_osint(phone_number)
        results['Phone Number Relevant Info'] = phone_relevant_info
        results['Phone Number Other Info'] = phone_other_info

    if instagram_username:
        instagram_info = get_instagram_info(instagram_username)
        results['Instagram Info'] = instagram_info

    if twitter_username:
        twitter_info = get_twitter_info(twitter_username)
        results['Twitter Info'] = twitter_info

    if github_username:
        github_info = get_github_info(github_username)
        results['GitHub Info'] = github_info

    if email:
        email_info = analyze_email_without_api(email)
        hunter_info = get_hunter_info(email)
        results['Email Info'] = email_info
        results['Hunter.io Info'] = hunter_info

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
