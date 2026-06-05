import os
import requests

# The endpoint extracted from your browser DevTools trace
URL = "https://www.hilton.com/graphql/customer?appName=dx-res-ui&appVersion=dx-res-ui%3A897156&operationName=hotel_shopAvailOptions_shopPropAvail&originalOpName=getShopAvail&bl=en&ctyhocn=LASDA"

# Extracted variables block modified strictly for your target dates: May 21 - 24, 2027
VARIABLES = {
    "guestLocationCountry": "US",
    "arrivalDate": "2027-05-21",       # Modified to target check-in
    "departureDate": "2027-05-24",     # Modified to target check-out
    "numAdults": 1,
    "numChildren": 0,
    "numRooms": 1,
    "displayCurrency": "USD",
    "ctyhocn": "LASDA",
    "language": "en",
    "guestId": None,
    "specialRates": {
        "aaa": False, "governmentMilitary": False, "hhonors": False, "lta": False,
        "pnd": "", "senior": False, "teamMember": False, "owner": False, "ownerHGV": False,
        "familyAndFriends": False, "travelAgent": False, "smb": False, "specialOffer": False,
        "specialOfferName": None
    },
    "pnd": None,
    "cacheId": "1ee53fea-f97e-4bb6-9219-3debe7d35d4d",
    "offerId": None,
    "knownGuest": False,
    "modifyingReservation": False,
    "currentlySelectedRoomTypeCode": None,
    "currentlySelectedRatePlanCode": None,
    "childAges": None,
    "adjoiningRoomStay": False,
    "includeCUCEligibility": False,
    "roomTypeSortInput": []
}

# The structural blueprint query payload expected by Hilton's GraphQL schema
QUERY = """query hotel_shopAvailOptions_shopPropAvail($arrivalDate: String!, $ctyhocn: String!, $departureDate: String!, $language: String!, $guestLocationCountry: String, $numAdults: Int!, $numChildren: Int!, $numRooms: Int!, $displayCurrency: String, $guestId: BigInt, $specialRates: ShopSpecialRateInput, $rateCategoryTokens: [String], $selectedRoomRateCodes: [ShopRoomRateCodeInput!], $ratePlanCodes: [String], $pnd: String, $offerId: BigInt, $cacheId: String!, $knownGuest: Boolean, $modifyingReservation: Boolean, $currentlySelectedRoomTypeCode: String, $currentlySelectedRatePlanCode: String, $childAges: [Int], $adjoiningRoomStay: Boolean, $programAccountId: BigInt, $roomTypeSortInput: [ShopRoomTypeSortInput!], $includeCUCEligibility: Boolean) {
  hotel(ctyhocn: $ctyhocn, language: $language) {
    roomTypes(filter: {accommodationCode_in: ["STD", "EXEC", "STE", "ACCS"]}) {
      roomTypeCode
      roomTypeName
    }
    shopAvail(cacheId: $cacheId, input: {guestLocationCountry: $guestLocationCountry, arrivalDate: $arrivalDate, departureDate: $departureDate, displayCurrency: $displayCurrency, numAdults: $numAdults, numChildren: $numChildren, numRooms: $numRooms, guestId: $guestId, specialRates: $specialRates, rateCategoryTokens: $rateCategoryTokens, selectedRoomRateCodes: $selectedRoomRateCodes, ratePlanCodes: $ratePlanCodes, knownGuest: $knownGuest, modifyingReservation: $modifyingReservation, childAges: $childAges, adjoiningRoomStay: $adjoiningRoomStay, programAccountId: $programAccountId, includeCUCEligibility: $includeCUCEligibility, includeGuests: true}) {
      statusCode
      roomTypes(sort: $roomTypeSortInput) {
        roomTypeCode
        roomTypeName
      }
    }
  }
}"""

HEADERS = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "dx-platform": "web",
    "origin": "https://www.hilton.com",
    "referer": "https://www.hilton.com/en/book/reservation/rooms/",
    "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# Pulling authorization details saved in Step 3 securely out of the server environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_alert(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(telegram_url, json=payload)
    except Exception as e:
        print(f"Failed to transmit Telegram alert: {e}")

def main():
    payload = {
        "operationName": "hotel_shopAvailOptions_shopPropAvail",
        "query": QUERY,
        "variables": VARIABLES
    }
    
    try:
        response = requests.post(URL, json=payload, headers=HEADERS, timeout=15)
        
        # If Hilton returns a 200, parse the JSON tree
        if response.status_code == 200:
            data = response.json()
            
            # Navigate deep into the JSON layers to see if a valid list of rooms exists
            hotel_data = data.get("data", {}).get("hotel")
            if hotel_data is None:
                print("Dates are completely locked: Server returned a null hotel object.")
                return
                
            shop_avail = hotel_data.get("shopAvail", {})
            rooms = shop_avail.get("roomTypes", [])
            
            if not rooms:
                msg = f"🚨🚨 HILTON ALERT: May 21-24, 2027 rooms are officially LIVE! Book right now: https://www.hilton.com/en/book/reservation/rooms/?ctyhocn=LASDAHW&arrivalDate=2027-05-21&departureDate=2027-05-24"
                send_alert(msg)
                print("Rooms found! Instant notification dispatched.")
            else:
                print("Checked: API connected, but the rooms list is empty (still unreleased).")
        else:
            print(f"Hilton API returned an error status code: {response.status_code}")
            
    except Exception as e:
        print(f"Network error during lookup task: {e}")

if __name__ == "__main__":
    # TEMPORARY TEST LINE: This bypasses Hilton entirely to test your Telegram secrets
    send_alert("Test Alert: GitHub Actions successfully talked to your Telegram bot!")
    
    main()
