import json
import boto3
import requests
import os

# Initialize AWS clients
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

# Environment variables for USPS
USPS_CONSUMER_KEY = os.environ.get("USPS_CONSUMER_KEY")
USPS_CONSUMER_SECRET = os.environ.get("USPS_CONSUMER_SECRET")
USPS_TOKEN_URL = "https://apis.usps.com/oauth2/v3/token"
USPS_BASE_URL = "https://apis.usps.com/addresses/v3/address"

# Smarty settings
SMARTY_BASE_URL = "https://us-street.api.smarty.com/street-address"

# DynamoDB Table for Caching
DYNAMODB_TABLE = "AddressValidationCache"
table = dynamodb.Table(DYNAMODB_TABLE)

def fetch_usps_token():
    """Fetches a short-lived access token from USPS using the Client Credentials flow."""
    data = {
        "grant_type": "client_credentials",
        "scope": "addresses",
        "client_id": USPS_CONSUMER_KEY,
        "client_secret": USPS_CONSUMER_SECRET
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    try:
        resp = requests.post(USPS_TOKEN_URL, data=data, headers=headers, timeout=10)
        resp.raise_for_status()
        token_response = resp.json()
        return token_response["access_token"]
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to obtain USPS token: {e}")

def validate_address_usps(address_data):
    """Validates an address using USPS API via OAuth Bearer token."""
    # Check minimal fields
    if not address_data or not all(k in address_data for k in ["streetAddress", "state", "ZIPCode"]):
        return {"error": "Invalid input. Must include 'streetAddress', 'state', and 'ZIPCode'."}

    # 1) Fetch access token
    try:
        token = fetch_usps_token()
    except RuntimeError as e:
        return {"error": str(e)}

    # 2) Build GET request
    params = {k: v for k, v in address_data.items() if v}
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(USPS_BASE_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"USPS validation failed: {e}"}

def validate_address_smarty(address_data):
    """
    Validates an address using Smarty's US Street API (single-address GET).
    Returns a dict with the standardized address or an error key if invalid.
    """
    SMARTY_AUTH_ID = os.environ.get("SMARTY_AUTH_ID")
    SMARTY_AUTH_TOKEN = os.environ.get("SMARTY_AUTH_TOKEN")
    if not SMARTY_AUTH_ID or not SMARTY_AUTH_TOKEN:
        return {"error": "Missing Smarty Auth ID/Token in environment variables."}
    
    # Build params
    street = address_data.get("streetAddress", "")
    city   = address_data.get("city", "")
    state  = address_data.get("state", "")
    zipc   = address_data.get("ZIPCode", "")

    params = {
        "auth-id": SMARTY_AUTH_ID,
        "auth-token": SMARTY_AUTH_TOKEN,
        "street": street,
        "city": city,
        "state": state,
        "zipcode": zipc,
        "candidates": 1,
        "match": "strict",
    }

    try:
        resp = requests.get(SMARTY_BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        result = resp.json()  # list of candidate addresses
        if not result:
            return {"error": "No valid Smarty address match."}
        return result[0]  # Return first candidate
    except requests.exceptions.RequestException as e:
        return {"error": f"Smarty validation failed: {e}"}

def validate_address_flow(address_data):
    """
    Attempt USPS first; if it fails or returns an error, fallback to Smarty.
    """
    usps_result = validate_address_usps(address_data)
    if "error" not in usps_result:
        return usps_result

    # If USPS gave an error, try Smarty
    smarty_result = validate_address_smarty(address_data)
    if "error" not in smarty_result:
        return smarty_result

    return {"error": "Neither USPS nor Smarty could validate this address."}

def lambda_handler(event, context):
    """AWS Lambda function entry point."""
    try:
        body = json.loads(event.get("body", "{}"))
        input_type = body.get("type")

        if not body:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No input received. Provide an address object or CSV."})
            }

        if input_type == "csv":
            bucket_name = body.get("bucket_name")
            file_key = body.get("file_key")
            if not bucket_name or not file_key:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Missing 'bucket_name' or 'file_key' for CSV."})
                }
            return process_csv(bucket_name, file_key)

        address_data = body.get("address")
        if not address_data:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing address input. Provide 'streetAddress', 'city', 'state', 'ZIPCode'."})
            }

        # ---- Call the fallback flow here instead of direct USPS ----
        validation_result = validate_address_flow(address_data)
        store_result_in_dynamodb(address_data, validation_result)

        return {
            "statusCode": 200,
            "body": json.dumps(validation_result)
        }

    except Exception as e:
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}

def process_csv(bucket_name, file_key):
    """
    Processes an uploaded CSV file for batch address validation.
    We'll do the fallback flow for each line.
    """
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    csv_data = obj["Body"].read().decode("utf-8").splitlines()

    results = []
    for line in csv_data[1:]:  # Skip header
        street, city, state, zipcode = line.split(",")
        address_data = {
            "streetAddress": street,
            "city": city,
            "state": state,
            "ZIPCode": zipcode
        }
        # Use fallback here as well
        validation_result = validate_address_flow(address_data)
        store_result_in_dynamodb(address_data, validation_result)
        results.append(validation_result)

    return {
        "statusCode": 200,
        "body": json.dumps(results)
    }

def store_result_in_dynamodb(address_data, validation_result):
    """Stores the validated address result in DynamoDB."""
    table.put_item(
        Item={
            "streetAddress": address_data.get("streetAddress", "Unknown"),
            "city": address_data.get("city", ""),
            "state": address_data.get("state", ""),
            "ZIPCode": address_data.get("ZIPCode", ""),
            "validationResult": validation_result
        }
    )