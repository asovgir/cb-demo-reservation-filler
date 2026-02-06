#!/usr/bin/env python3

import os
import json
import requests
import random
import string
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)

# SECURITY: Secret key for session encryption
# PRODUCTION: Set SECRET_KEY environment variable
# DEVELOPMENT: Uses default below (CHANGE THIS in production!)
DEFAULT_DEV_KEY = 'dev-key-UNSAFE-change-in-production-' + ''.join(random.choices('abcdef0123456789', k=32))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', DEFAULT_DEV_KEY)

# Warn if using default key
if not os.environ.get('SECRET_KEY'):
    print("\n" + "!"*60)
    print("WARNING: Using default SECRET_KEY for development only!")
    print("PRODUCTION: Set SECRET_KEY environment variable")
    print("!"*60 + "\n")

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# Allow longer response times for bulk reservation creation
app.config['TIMEOUT'] = 3600  # 1 hour timeout
# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

def get_credentials():
    """Get credentials from session storage"""
    return {
        'access_token': session.get('access_token'),
        'property_id': session.get('property_id', '6000')
    }

# API URLs
ROOM_TYPES_URL = "https://api.cloudbeds.com/api/v1.3/getRoomTypes"
POST_RESERVATION_URL = "https://api.cloudbeds.com/api/v1.3/postReservation"
GET_SOURCES_URL = "https://api.cloudbeds.com/api/v1.3/getSources"

# Cache for sources to avoid repeated API calls
_cached_sources = None

def get_available_sources(credentials):
    """Fetch available sources from the API and cache them"""
    global _cached_sources

    if _cached_sources is not None:
        print(f"Using cached source: {_cached_sources}", flush=True)
        return _cached_sources

    try:
        print("=" * 60, flush=True)
        print("FETCHING AVAILABLE SOURCES FROM API", flush=True)
        print("=" * 60, flush=True)
        result = make_api_call(GET_SOURCES_URL, {'propertyID': credentials['property_id']}, credentials)

        print(f"DEBUG - getSources API result success: {result.get('success')}", flush=True)
        print(f"DEBUG - getSources API result keys: {result.keys()}", flush=True)
        print(f"DEBUG - getSources API full response: {json.dumps(result, indent=2)}", flush=True)

        if result['success'] and 'data' in result:
            sources = result['data']
            print(f"DEBUG - Sources data type: {type(sources)}", flush=True)
            print(f"DEBUG - Sources data: {json.dumps(sources, indent=2)}", flush=True)

            if sources and len(sources) > 0:
                print(f"DEBUG - Found {len(sources)} available sources", flush=True)

                # List all available sources
                print("\nAVAILABLE SOURCES:", flush=True)
                for idx, source in enumerate(sources):
                    print(f"  {idx+1}. ID: {source.get('sourceID')} - Name: {source.get('sourceName', 'Unknown')}", flush=True)

                # Return the first source ID or a preferred one
                for source in sources:
                    if source.get('sourceID'):
                        selected_source = source.get('sourceID')
                        _cached_sources = selected_source
                        print(f"\n✓ SELECTED SOURCE: {selected_source} - {source.get('sourceName', 'Unknown')}", flush=True)
                        print("=" * 60, flush=True)
                        return selected_source
            else:
                print("WARNING - Sources data is empty or has 0 length", flush=True)
        else:
            print(f"WARNING - API call failed or no data. Success: {result.get('success')}, Has 'data': {'data' in result}", flush=True)

        # Fallback to the known working source ID
        print("\nWARNING: No sources found in API response", flush=True)
        print("Using fallback source ID: 'ss-123298-1'", flush=True)
        print("=" * 60, flush=True)
        _cached_sources = 'ss-123298-1'
        return 'ss-123298-1'

    except Exception as e:
        print(f"\nERROR fetching sources: {e}", flush=True)
        import traceback
        traceback.print_exc()
        # Fallback to the known working source ID
        print("Using fallback source ID due to error: 'ss-123298-1'", flush=True)
        print("=" * 60, flush=True)
        _cached_sources = 'ss-123298-1'
        return 'ss-123298-1'

def make_api_call(url, params, credentials, method='GET', data=None, use_form_data=False, retry_count=0, max_retries=2):
    if use_form_data:
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive"
        }
    else:
        headers = {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Connection": "keep-alive"
        }

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=60)
        else:
            if use_form_data:
                response = requests.post(url, headers=headers, params=params, data=data, timeout=60)
            else:
                response = requests.post(url, headers=headers, params=params, json=data, timeout=60)

        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            return {'success': True, 'data': data}
        else:
            error_msg = f"HTTP {response.status_code}"
            try:
                error_data = response.json()
                error_msg = error_data.get('message', error_msg)
                print(f"API Error response: {error_data}", flush=True)
            except:
                print(f"API Error - no JSON response: {response.text}", flush=True)
                pass
            return {'success': False, 'error': error_msg}
    except requests.exceptions.Timeout:
        if retry_count < max_retries:
            print(f"⚠ API call timed out, retrying ({retry_count + 1}/{max_retries})...", flush=True)
            time.sleep(2)
            return make_api_call(url, params, credentials, method, data, use_form_data, retry_count + 1, max_retries)
        print(f"✗ API call timed out after {max_retries} retries", flush=True)
        return {'success': False, 'error': f"Request timed out after {max_retries} retries"}
    except requests.exceptions.ConnectionError as e:
        if retry_count < max_retries:
            print(f"⚠ Connection error, retrying ({retry_count + 1}/{max_retries})...", flush=True)
            time.sleep(2)
            return make_api_call(url, params, credentials, method, data, use_form_data, retry_count + 1, max_retries)
        print(f"✗ Connection error after {max_retries} retries", flush=True)
        return {'success': False, 'error': "Connection error - check your internet connection"}
    except Exception as e:
        print(f"✗ Unexpected error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': f"Connection error: {str(e)}"}

def generate_random_name():
    """Generate random first and last names"""
    first_names = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
        "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
        "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Nancy", "Daniel", "Lisa",
        "Matthew", "Betty", "Anthony", "Helen", "Mark", "Sandra", "Donald", "Donna",
        "Steven", "Carol", "Paul", "Ruth", "Andrew", "Sharon", "Kenneth", "Michelle",
        "Joshua", "Laura", "Kevin", "Sarah", "Brian", "Kimberly", "George", "Deborah",
        "Edward", "Dorothy", "Ronald", "Lisa", "Timothy", "Nancy", "Jason", "Karen"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
        "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
        "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
        "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
        "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
        "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker"
    ]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    
    return first_name, last_name

def generate_random_email(first_name, last_name):
    """Generate email ending with @example.com"""
    # Create variations of email formats
    formats = [
        f"{first_name.lower()}.{last_name.lower()}",
        f"{first_name.lower()}{last_name.lower()}",
        f"{first_name[0].lower()}{last_name.lower()}",
        f"{first_name.lower()}{last_name[0].lower()}",
        f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}"
    ]
    
    email_prefix = random.choice(formats)
    return f"{email_prefix}@example.com"

def generate_reservation_dates(start_date, end_date):
    """Generate random check-in and check-out dates within the range with random 1-7 night stays"""
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')

    # Generate random stay length first (1-7 nights)
    stay_length = random.randint(1, 7)

    # Calculate the range of possible check-in dates
    # Ensure there's room for the selected stay length
    max_checkin_date = end_dt - timedelta(days=stay_length)

    if start_dt > max_checkin_date:
        # If the date range is too small for this stay length, adjust
        checkin_date = start_dt
        # Adjust stay length to fit within available dates
        max_possible_stay = (end_dt - start_dt).days
        if max_possible_stay > 0:
            stay_length = min(stay_length, max_possible_stay)
        else:
            stay_length = 1
    else:
        # Random check-in date within the valid range
        days_diff = (max_checkin_date - start_dt).days
        random_days = random.randint(0, max(0, days_diff))
        checkin_date = start_dt + timedelta(days=random_days)

    checkout_date = checkin_date + timedelta(days=stay_length)

    # Make sure checkout doesn't exceed the end date
    if checkout_date > end_dt:
        checkout_date = end_dt
        stay_length = (checkout_date - checkin_date).days

    # Return dates plus the actual stay length for logging
    return checkin_date.strftime('%Y-%m-%d'), checkout_date.strftime('%Y-%m-%d'), stay_length

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/save-settings', methods=['POST'])
def save_settings():
    try:
        data = request.get_json()
        session['access_token'] = data.get('access_token', '').strip()
        session['property_id'] = data.get('property_id', '6000').strip()
        session.permanent = True
        return jsonify({'success': True, 'message': 'Settings saved successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get-settings')
def get_settings():
    return jsonify({
        'success': True,
        'data': {
            'access_token': session.get('access_token', ''),
            'property_id': session.get('property_id', '6000')
        }
    })

@app.route('/api/test-connection')
def test_connection():
    try:
        form_access_token = request.args.get('access_token')
        form_property_id = request.args.get('property_id')
        
        if form_access_token and form_property_id:
            credentials = {
                'access_token': form_access_token.strip(),
                'property_id': form_property_id.strip()
            }
        else:
            credentials = get_credentials()
        
        if not credentials['access_token']:
            return jsonify({'success': False, 'error': 'Please configure your access token first.'})
        
        result = make_api_call(ROOM_TYPES_URL, {'propertyID': credentials['property_id']}, credentials)
        
        if result['success']:
            return jsonify({'success': True, 'message': 'Connection successful!'})
        else:
            return jsonify({'success': False, 'error': result['error']})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'})

@app.route('/api/room-types')
def get_room_types():
    try:
        credentials = get_credentials()
        
        if not credentials['access_token']:
            return jsonify({'success': False, 'error': 'Access token not configured'})
        
        response = make_api_call(ROOM_TYPES_URL, {'propertyID': credentials['property_id']}, credentials)
        
        if not response['success']:
            return jsonify({'success': False, 'error': response['error']})
        
        # Extract room types data
        data = response['data']
        room_types = []
        
        if isinstance(data, dict) and 'data' in data:
            room_types = data['data']
        elif isinstance(data, list):
            room_types = data
        
        # Process room types to extract needed fields
        processed_room_types = []
        for rt in room_types:
            if rt:
                processed_room_types.append({
                    'roomTypeID': rt.get('roomTypeID'),
                    'roomTypeName': rt.get('roomTypeName'),
                    'roomTypeUnits': rt.get('roomTypeUnits', 0),
                    'maxGuests': rt.get('maxGuests', 1)
                })
        
        return jsonify({
            'success': True,
            'data': processed_room_types
        })
        
    except Exception as e:
        print(f"Error in get_room_types: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/create-reservations', methods=['POST'])
def create_reservations():
    try:
        print("\n" + "="*80, flush=True)
        print("STARTING RESERVATION CREATION PROCESS", flush=True)
        print("="*80, flush=True)

        credentials = get_credentials()

        if not credentials['access_token']:
            return jsonify({'success': False, 'error': 'Access token not configured'})

        # Get available source ID
        source_id = get_available_sources(credentials)
        print(f"\n→ Will use sourceID for all reservations: {source_id}", flush=True)

        if not source_id:
            error_msg = "CRITICAL: No source ID available! Cannot create reservations."
            print(f"\n✗ {error_msg}", flush=True)
            return jsonify({'success': False, 'error': error_msg})

        data = request.get_json()
        room_type_configs = data.get('roomTypeConfigs', [])
        start_date = data.get('startDate')
        end_date = data.get('endDate')

        if not start_date or not end_date:
            return jsonify({'success': False, 'error': 'Start date and end date are required'})

        print(f"→ Date Range: {start_date} to {end_date}", flush=True)
        print(f"→ Room Types to Process: {len(room_type_configs)}", flush=True)

        # Calculate total expected reservations using the new formula
        # This is just for estimation - actual calculation happens in the loop
        start_dt_calc = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt_calc = datetime.strptime(end_date, '%Y-%m-%d')
        num_days_calc = (end_dt_calc - start_dt_calc).days
        # CRITICAL: Must match actual average for uniform distribution 1-7 nights = 4.0 nights
        average_stay_length_calc = 4.0

        total_expected = 0
        for cfg in room_type_configs:
            if cfg.get('percentage', 0) > 0:
                total_room_nights = num_days_calc * cfg.get('roomTypeUnits', 0)
                target_room_nights = total_room_nights * (cfg.get('percentage', 0) / 100)
                reservations_for_room_type = max(1, int(target_room_nights / average_stay_length_calc))
                total_expected += reservations_for_room_type

        print(f"→ Total Reservations to Create (estimated): {total_expected}", flush=True)
        print(f"→ Estimated time: ~{int(total_expected * 0.3 / 60)} minutes ({total_expected * 0.3:.0f} seconds with 0.3s delays)\n", flush=True)

        results = []
        total_created = 0
        total_errors = 0
        
        # Calculate date range in days
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        num_days = (end_dt - start_dt).days

        print(f"→ Date range: {num_days} days ({start_date} to {end_date})", flush=True)

        for config in room_type_configs:
            room_type_id = config.get('roomTypeID')
            room_type_name = config.get('roomTypeName')
            room_type_units = config.get('roomTypeUnits', 0)
            percentage = config.get('percentage', 0)

            if percentage <= 0:
                continue

            # Calculate number of reservations to create based on room-nights
            # Formula: (total room-nights available * percentage) / actual average stay length
            # This ensures the occupancy percentage is achieved on EACH DATE
            #
            # Example: 100 rooms, 7 days, 50% target occupancy
            #   - Total room-nights available: 7 * 100 = 700
            #   - Target: 50% * 700 = 350 room-nights
            #   - Actual average stay for random 1-7 nights: (1+2+3+4+5+6+7)/7 = 4 nights
            #   - Reservations needed: 350 / 4 = 87.5 ≈ 88 reservations
            #   - Result: 88 reservations * 4 nights avg = 352 room-nights / 7 days = 50.3 rooms per night ≈ 50%

            total_room_nights_available = num_days * room_type_units
            target_room_nights = total_room_nights_available * (percentage / 100)

            # CRITICAL: Use the actual mathematical average for uniform random distribution (1-7 nights)
            # The mathematical expectation is (1+2+3+4+5+6+7)/7 = 4 nights
            # Using any other value will cause occupancy mismatch!
            average_stay_length = 4.0
            num_reservations = max(1, int(round(target_room_nights / average_stay_length)))

            # Add explanation in the log
            print(f"\n{'='*80}", flush=True)
            print(f"CALCULATION FOR {room_type_name}:", flush=True)
            print(f"  • Room Units: {room_type_units}", flush=True)
            print(f"  • Date Range: {num_days} days", flush=True)
            print(f"  • Total Room-Nights Available: {total_room_nights_available}", flush=True)
            print(f"  • Target Occupancy PER NIGHT: {percentage}%", flush=True)
            print(f"  • Target Rooms Per Night: {room_type_units * (percentage / 100):.1f} rooms", flush=True)
            print(f"  • Total Room-Nights to Fill: {target_room_nights:.1f}", flush=True)
            print(f"  • Average Stay Length (1-7 nights uniform): {average_stay_length} nights", flush=True)
            print(f"  • Reservations to Create: {num_reservations}", flush=True)
            expected_occupancy = (num_reservations * average_stay_length / total_room_nights_available * 100)
            expected_rooms_per_night = num_reservations * average_stay_length / num_days
            print(f"  • Expected Result: {expected_rooms_per_night:.1f} rooms per night ({expected_occupancy:.1f}% occupancy)", flush=True)
            print(f"{'='*80}", flush=True)
            
            room_results = {
                'roomTypeID': room_type_id,
                'roomTypeName': room_type_name,
                'requested': num_reservations,
                'created': 0,
                'errors': [],
                'stay_lengths': []  # Track stay lengths for statistics
            }
            
            # Create reservations for this room type
            print(f"\n{'='*80}", flush=True)
            print(f"STARTING CREATION FOR: {room_type_name}", flush=True)
            print(f"{'='*80}\n", flush=True)

            for i in range(num_reservations):
                try:
                    print(f"\n[{room_type_name}] Processing reservation {i+1}/{num_reservations}", flush=True)

                    # Calculate overall progress
                    total_completed_so_far = total_created + total_errors
                    if total_expected > 0:
                        progress_pct = int((total_completed_so_far / total_expected) * 100)
                        print(f"Overall progress: {total_completed_so_far}/{total_expected} ({progress_pct}% complete)", flush=True)
                    else:
                        print(f"Overall progress: {total_completed_so_far} completed", flush=True)

                    # Generate random guest data
                    first_name, last_name = generate_random_name()
                    email = generate_random_email(first_name, last_name)
                    checkin_date, checkout_date, stay_length = generate_reservation_dates(start_date, end_date)

                    # Prepare reservation data according to Cloudbeds API schema
                    import json

                    reservation_data = {
                        'propertyID': credentials['property_id'],
                        'startDate': checkin_date,
                        'endDate': checkout_date,
                        'guestFirstName': first_name,
                        'guestLastName': last_name,
                        'guestEmail': email,
                        'guestCountry': 'US',
                        'guestZip': '12345',
                        'guestPhone': f'{random.randint(2000000000, 9999999999)}',
                        'guestGender': 'M',  # Default gender
                        'paymentMethod': 'ebanking',
                        'sourceID': source_id,
                        'thirdPartyIdentifier': f'demo-{random.randint(10000, 99999)}',
                        'sendEmailConfirmation': False,
                        # Convert arrays to JSON strings as required by the API
                        'rooms': json.dumps([{"roomTypeID": room_type_id, "quantity": 1}]),
                        'adults': json.dumps([{"quantity": 1, "roomTypeID": room_type_id}]),
                        'children': json.dumps([{"roomTypeID": room_type_id, "quantity": 0}])
                    }

                    # Make API call to create reservation
                    print(f"→ Creating reservation for {first_name} {last_name}", flush=True)
                    print(f"  Check-in: {checkin_date} | Check-out: {checkout_date} | Stay: {stay_length} night{'s' if stay_length != 1 else ''}", flush=True)
                    print(f"  Using sourceID: {source_id}", flush=True)

                    result = make_api_call(
                        POST_RESERVATION_URL,
                        {},  # No query params for POST
                        credentials,
                        method='POST',
                        data=reservation_data,
                        use_form_data=True  # Use form-encoded data for postReservation
                    )

                    if result['success']:
                        reservation_id = 'N/A'
                        if 'data' in result and result['data']:
                            reservation_id = result['data'].get('reservationID', 'N/A')
                        print(f"✓ SUCCESS: Reservation {i+1}/{num_reservations} created (ID: {reservation_id}) | Total: {total_created + 1}", flush=True)
                        room_results['created'] += 1
                        room_results['stay_lengths'].append(stay_length)
                        total_created += 1
                    else:
                        error_msg = f"Reservation {i+1}: {result['error']}"
                        print(f"✗ ERROR: {error_msg}", flush=True)
                        room_results['errors'].append(error_msg)
                        total_errors += 1

                    # Add delay between API calls to prevent rate limiting (0.3 seconds)
                    # This ensures we don't hit API rate limits while keeping total time reasonable
                    if i < num_reservations - 1:  # Don't delay after the last reservation
                        time.sleep(0.3)  # 300ms delay - fast enough to avoid HTTP timeout, slow enough to avoid rate limits

                except Exception as e:
                    error_msg = f"Reservation {i+1}: {str(e)}"
                    print(f"✗ EXCEPTION: {error_msg}", flush=True)
                    import traceback
                    traceback.print_exc()
                    room_results['errors'].append(error_msg)
                    total_errors += 1
                    # Continue to next reservation even if this one failed
                    print(f"→ Continuing to next reservation despite error...", flush=True)
                    continue
            
            results.append(room_results)

        # Print final summary
        print(f"\n{'='*80}", flush=True)
        print("RESERVATION CREATION COMPLETE - FINAL SUMMARY", flush=True)
        print(f"{'='*80}", flush=True)
        print(f"✓ Total Reservations Successfully Created: {total_created}", flush=True)
        print(f"✗ Total Errors: {total_errors}", flush=True)
        print(f"\nBreakdown by Room Type:", flush=True)
        for result in results:
            print(f"  - {result['roomTypeName']}: {result['created']}/{result['requested']} created", flush=True)
            if result['errors']:
                print(f"    Errors: {len(result['errors'])}", flush=True)

            # Show stay length statistics
            if result['stay_lengths']:
                avg_stay = sum(result['stay_lengths']) / len(result['stay_lengths'])
                min_stay = min(result['stay_lengths'])
                max_stay = max(result['stay_lengths'])
                print(f"    Stay lengths: {min_stay}-{max_stay} nights (avg: {avg_stay:.1f} nights)", flush=True)

                # Show distribution
                from collections import Counter
                stay_counts = Counter(result['stay_lengths'])
                distribution = ', '.join([f"{nights}n: {count}" for nights, count in sorted(stay_counts.items())])
                print(f"    Distribution: {distribution}", flush=True)
        print(f"{'='*80}\n", flush=True)

        return jsonify({
            'success': True,
            'data': {
                'results': results,
                'summary': {
                    'total_created': total_created,
                    'total_errors': total_errors
                }
            }
        })
        
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"CRITICAL ERROR in create_reservations")
        print(f"{'='*80}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*80}\n")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Get port from environment variable (for cloud hosting) or use 5000 for local
    port = int(os.environ.get('PORT', 5000))
    # Get debug mode from environment (disable in production)
    debug = os.environ.get('FLASK_ENV') != 'production'

    if debug:
        print("\nCloudbeds Reservation Creator - Web App")
        print("=" * 50)
        print(f"Starting server on http://localhost:{port}")
        print("Close this window to stop the application\n")
        print("NOTE: Long-running reservation creation supported")
        print("      Keep this console window open to monitor progress\n")

    try:
        # Run with threaded mode to handle long-running requests better
        # In production, use 0.0.0.0 to allow external connections
        host = '0.0.0.0' if not debug else '127.0.0.1'
        app.run(host=host, port=port, debug=debug, threaded=True)
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"\nError starting application: {e}")
        if debug:
            input("Press Enter to close...")