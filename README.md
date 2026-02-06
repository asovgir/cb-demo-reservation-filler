# Cloudbeds Reservation Creator

A web application for creating bulk reservations in Cloudbeds properties. Set custom occupancy percentages for each room type, and the app automatically generates realistic reservations with random guest data and varied stay lengths (1-7 nights).

## Features

- **Bulk Reservation Creation**: Create multiple reservations at once across different room types
- **Occupancy Control**: Set target occupancy percentages for each room type
- **Realistic Data**: Random guest names, emails, dates, and stay lengths (1-7 nights)
- **Smart Calculation**: Automatically calculates the number of reservations needed based on:
  - Room units available
  - Date range
  - Target occupancy percentage
  - Average stay length (uniform 1-7 nights = 4 nights average)
- **Progress Tracking**: Real-time console logging with detailed progress updates
- **Error Resilience**: Continues creating reservations even if individual ones fail
- **Rate Limiting Protection**: Built-in delays to prevent API rate limiting

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/asovgir/cb-demo-reservation-filler.git
   cd cb-demo-reservation-filler
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

4. **Access the app** at http://localhost:5000

## Configuration

The app uses browser sessions to store your Cloudbeds API credentials:
- **Access Token**: Your Cloudbeds API access token
- **Property ID**: Your property ID (default: 6000)

Credentials are stored securely in the session and expire after 7 days of inactivity. No credentials are saved to disk or committed to git.

## How to Use

1. **Configure API Access**:
   - Enter your Cloudbeds API access token
   - Enter your property ID
   - Click "Connect" to test the connection

2. **Set Date Range**:
   - Select start and end dates for reservations
   - Click "Load Room Types"

3. **Set Occupancy Percentages**:
   - For each room type, enter the desired occupancy percentage (0-100%)
   - The app calculates how many reservations to create based on:
     - Number of units
     - Number of days in date range
     - Target occupancy percentage
     - Average stay length (2 nights)

4. **Create Reservations**:
   - Click "Create Reservations"
   - Monitor progress in the browser and server console
   - View detailed results when complete

## Technical Details

### Reservation Calculation

The app uses a room-nights formula to achieve target occupancy:

```
Total Room-Nights Available = Days × Units
Target Room-Nights = Total Room-Nights × Percentage
Reservations Needed = Target Room-Nights ÷ Average Stay Length (2 nights)
```

**Example**:
- 10 units, 7 days, 50% occupancy
- Room-nights available: 7 × 10 = 70
- Target room-nights: 70 × 50% = 35
- Reservations to create: 35 ÷ 2 = 18 reservations

Each reservation gets a random 1-7 night stay, with random check-in dates distributed across the date range.

### Rate Limiting

The app includes a 0.3-second delay between API calls to prevent rate limiting while keeping total execution time reasonable.

### Error Handling

- Automatic retry on timeout/connection errors (up to 2 retries)
- Continues creating reservations even if individual ones fail
- Detailed error logging and reporting

## Requirements

- Python 3.11 or higher
- Cloudbeds API access token
- Active internet connection

## Support

For issues or questions about the Cloudbeds API, refer to the [Cloudbeds API Documentation](https://hotels.cloudbeds.com/api/docs/).

## Security

- No credentials are stored in the code
- All sensitive data uses encrypted session storage
- Sessions expire after 7 days of inactivity
- Safe to commit to public repositories

See `SECURITY.md` for more details.

## License

This is a utility tool for Cloudbeds property management. Use at your own risk and ensure you have proper authorization to create reservations in your property.
