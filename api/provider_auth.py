import requests
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_provider_details(provider_id: str, token: str, type: str, ci_session: Optional[str] = None) -> Dict:
    """
    Get provider details from the BigToe API
    """
    url = "https://bigtoe.app/app/Provider_AI/getProviderDetails"
    
    headers = {
        'Content-Type': 'application/json',
    }

    # Add cookies if session is provided
    cookies = {}
    if ci_session:
        cookies['ci_session'] = ci_session
    
    payload = {
        "provider_id": provider_id,
        "token": token,
        "type": type
    }


    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            cookies=cookies
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "ResponseCode": 0,
            "ResponseMessage": f"Error: {str(e)}",
            "Comments": "Failed to fetch provider details",
            "Result": None
        }
    except ValueError as e:  # JSON decode error
        return {
            "ResponseCode": 0,
            "ResponseMessage": "Invalid response format",
            "Comments": "Failed to parse provider details",
            "Result": None
        }

def get_initial_message(provider_details: Optional[Dict] = None) -> str:
    """
    Generate initial message based on provider authentication status
    """
    default_message = "Hey! I'm BigToe AI assistant. How can I help you today?"

    print("provider_details", provider_details)
    if (provider_details and 
        provider_details.get("ResponseCode") == 1 and 
        provider_details.get("Result")):
        provider_name = provider_details["Result"].get("firstname", "")
        return f"Hey {provider_name}, I'm BigToe AI assistant. Let me know what you need assistance with!"
    
    return default_message 

def get_sessions_details(provider_id: str, token: str, type: str, ci_session: Optional[str] = None) -> Dict:
    """
    Get provider details from the BigToe API
    """
    url = "https://bigtoe.app/app/Provider_AI/getProviderPreviousSessions"
    
    headers = {
        'Content-Type': 'application/json',
    }

    # Add cookies if session is provided
    cookies = {}
    if ci_session:
        cookies['ci_session'] = ci_session
    
    payload = {
        "provider_id": provider_id,
        "token": token,
        "type": type
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            cookies=cookies
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "ResponseCode": 0,
            "ResponseMessage": f"Error: {str(e)}",
            "Comments": "Failed to fetch sessions details",
            "Result": None
        }
    except ValueError as e:  # JSON decode error
        return {
            "ResponseCode": 0,
            "ResponseMessage": "Invalid response format",
            "Comments": "Failed to parse sessions details",
            "Result": None
        }