# Local Setup Guide

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Git (optional, for cloning)

### Installation Steps

1. **Get the code**:

   If you have git:
   ```bash
   git clone https://github.com/asovgir/cb-demo-reservation-filler.git
   cd cb-demo-reservation-filler
   ```

   Or download the ZIP from GitHub and extract it.

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

4. **Access the app**:
   Open your browser to http://localhost:5000

## First-Time Setup

When you first open the app:

1. **Enter your Cloudbeds API credentials**:
   - Access Token: Your Cloudbeds API access token
   - Property ID: Your property ID (default is 6000)

2. **Click "Connect"** to test the connection

3. **Set your date range** for reservations

4. **Click "Load Room Types"** to fetch your property's room types

5. **Set occupancy percentages** for each room type

6. **Click "Create Reservations"** and monitor progress in the console

## Troubleshooting

### "Module not found" errors
Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

### Port 5000 already in use
Change the port by setting an environment variable:
```bash
# Windows
set PORT=8000
python main.py

# Mac/Linux
PORT=8000 python main.py
```

### Connection issues
- Verify your Cloudbeds API token is valid
- Check your internet connection
- Ensure the property ID is correct

### Reservations stopping early
- Check the console output for specific errors
- The app includes automatic retries for network issues
- Rate limiting protection (0.3s delay between reservations)

## Console Output

The application provides detailed console logging:
- Source ID selection and validation
- Per-reservation progress tracking
- Success/error status for each reservation
- Final summary with statistics
- Stay length distribution

Keep the console window open to monitor the reservation creation process.

## Stopping the Application

To stop the server:
- Press `Ctrl+C` in the terminal/console window
- Or simply close the terminal window

## Data Storage

- **Credentials**: Stored in encrypted browser sessions only
- **No local files**: Nothing is saved to your computer
- **Session expiry**: 7 days of inactivity
- **Safe to share**: No credentials in the code

## Need Help?

- **Cloudbeds API Docs**: https://hotels.cloudbeds.com/api/docs/
- **GitHub Issues**: https://github.com/asovgir/cb-demo-reservation-filler/issues
