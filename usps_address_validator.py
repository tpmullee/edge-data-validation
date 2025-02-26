#!/usr/bin/env python3
import requests
import argparse
import logging
import xml.etree.ElementTree as ET
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

USPS_API_URL = "https://secure.shippingapis.com/ShippingAPI.dll"

def build_request_xml(user_id, street, city, state, zip_code):
    """
    Build XML request for USPS Address Validation API.
    """
    xml = f"""<AddressValidateRequest USERID="{user_id}">
        <Revision>1</Revision>
        <Address ID="0">
            <Address1></Address1>
            <Address2>{street}</Address2>
            <City>{city}</City>
            <State>{state}</State>
            <Zip5>{zip_code}</Zip5>
            <Zip4></Zip4>
        </Address>
    </AddressValidateRequest>"""
    return xml

def validate_address(user_id, street, city, state, zip_code):
    """
    Validates and corrects an address using USPS API.
    """
    xml_request = build_request_xml(user_id, street, city, state, zip_code)
    params = {
        'API': 'Verify',
        'XML': xml_request
    }
    try:
        response = requests.get(USPS_API_URL, params=params)
        response.raise_for_status()
        # Parse XML response
        root = ET.fromstring(response.text)
        error = root.find('.//Error')
        if error is not None:
            description = error.find('Description').text
            logging.error(f"USPS API Error: {description}")
            return None
        corrected_address = {}
        address = root.find('.//Address')
        if address is not None:
            corrected_address['address1'] = address.findtext('Address1', default='')
            corrected_address['address2'] = address.findtext('Address2', default='')
            corrected_address['city'] = address.findtext('City', default='')
            corrected_address['state'] = address.findtext('State', default='')
            corrected_address['zip5'] = address.findtext('Zip5', default='')
            corrected_address['zip4'] = address.findtext('Zip4', default='')
            return corrected_address
    except Exception as e:
        logging.error(f"Error validating address: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="USPS Address Validation Utility")
    parser.add_argument("--street", required=True, help="Street address")
    parser.add_argument("--city", required=True, help="City name")
    parser.add_argument("--state", required=True, help="State abbreviation")
    parser.add_argument("--zip", required=True, help="ZIP code")
    parser.add_argument("--user_id", required=False, help="USPS API User ID", default=os.getenv('USPS_USER_ID'))
    args = parser.parse_args()

    if not args.user_id:
        logging.error("USPS User ID must be provided via --user_id or USPS_USER_ID environment variable.")
        return

    corrected = validate_address(args.user_id, args.street, args.city, args.state, args.zip)
    if corrected:
        logging.info("Address validation successful. Corrected address:")
        for key, value in corrected.items():
            print(f"{key}: {value}")
    else:
        logging.error("Address validation failed.")

if __name__ == "__main__":
    main()
