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
  - Average stay length (configurable)
- **Progress Tracking**: Real-time console logging with detailed progress updates
- **Error Resilience**: Continues creating reservations even if individual ones fail
- **Rate Limiting Protection**: Built-in delays to prevent API rate limiting

## Deployment Options

### Option 1: Deploy to Render (Recommended - Free Tier Available)

1. **Create a Render account** at https://render.com

2. **Create a new Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository (or deploy from this directory)
   - Configure the service:
     - **Name**: `cloudbeds-reservation-creator`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn main:app --timeout 3600 --workers 2 --threads 4 --worker-class gthread`
     - **Instance Type**: `Free` (or higher for better performance)

3. **Set Environment Variables**:
   - Go to "Environment" tab
   - Add:
     - `FLASK_ENV` = `production`
     - `SECRET_KEY` = `your-random-secret-key-here` (generate a random string)
     - `PYTHON_VERSION` = `3.11.7`

4. **Deploy**: Click "Create Web Service" and wait for deployment to complete

5. **Access your app** at the URL provided by Render (e.g., `https://your-app-name.onrender.com`)

### Option 2: Deploy to Heroku

1. **Install Heroku CLI** from https://devcenter.heroku.com/articles/heroku-cli

2. **Login to Heroku**:
   ```bash
   heroku login
   ```

3. **Create a new Heroku app**:
   ```bash
   heroku create your-app-name
   ```

4. **Set environment variables**:
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-random-secret-key-here
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```
   (or `git push heroku master` if your branch is named master)

6. **Open your app**:
   ```bash
   heroku open
   ```

### Option 3: Deploy to Railway

1. **Create a Railway account** at https://railway.app

2. **Create a new project**:
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

3. **Railway will automatically detect** the Python app and deploy it

4. **Set Environment Variables**:
   - Go to your project → "Variables" tab
   - Add:
     - `FLASK_ENV` = `production`
     - `SECRET_KEY` = `your-random-secret-key-here`

5. **Access your app** at the URL provided by Railway

### Option 4: Deploy to Google Cloud Run

1. **Install Google Cloud SDK** from https://cloud.google.com/sdk/docs/install

2. **Create a Dockerfile** (if not already present):
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   ENV PORT=8080
   ENV FLASK_ENV=production
   CMD exec gunicorn main:app --bind :$PORT --timeout 3600 --workers 2 --threads 4 --worker-class gthread
   ```

3. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy cloudbeds-creator --source . --region us-central1 --allow-unauthenticated
   ```

## Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```

3. **Access the app** at http://localhost:5000

## Configuration

### Environment Variables

- `SECRET_KEY`: Secret key for Flask sessions (required in production)
- `FLASK_ENV`: Set to `production` in production environments
- `PORT`: Port to run the application on (auto-detected from hosting platform)

### Application Settings

The app uses browser sessions to store your Cloudbeds API credentials:
- **Access Token**: Your Cloudbeds API access token
- **Property ID**: Your property ID (default: 6000)

These are stored securely in the session and expire after 7 days of inactivity.

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

## Support

For issues or questions about the Cloudbeds API, refer to the [Cloudbeds API Documentation](https://hotels.cloudbeds.com/api/docs/).

## License

This is a utility tool for Cloudbeds property management. Use at your own risk and ensure you have proper authorization to create reservations in your property.
