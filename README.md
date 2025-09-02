# YouTube Playlist Exporter

A simple and efficient web application to export the details of any public YouTube playlist into a downloadable CSV file. Just paste the playlist URL, and get a detailed spreadsheet with video titles, URLs, view counts, likes, and more.

## Features

- **Comprehensive Data Export**: Extracts video title, channel, published date, views, likes, duration, and direct URL.
- **High Accuracy**: Uses paginated API calls to ensure every single video from the playlist is fetched, no matter the size.
- **Automatic File Naming**: The downloaded CSV is automatically named after the playlist's title.
- **Instant Download**: The file is generated in memory and downloaded directly to your browser.
- **Clean & Modern UI**: A simple, dark-themed, and responsive user interface.
- **Easy Deployment**: Ready to be deployed on serverless platforms like Vercel.

## Technology Stack

- **Backend**: Python
- **Framework**: Flask
- **YouTube API**: google-api-python-client
- **Data Processing**: Pandas
- **Frontend**: HTML, CSS, JavaScript (no frameworks)
- **Deployment**: Vercel

## Local Setup and Installation

Follow these steps to run the project on your local machine.

### Prerequisites

- Python 3.7+
- A web browser

### 1. Clone the Repository

```bash
git clone https://github.com/durgesh-kushwaha/youtube-exporter.git
cd youtube-exporter
```

### 2. Get a YouTube Data API Key

You need an API key to fetch data from YouTube.

- Go to the [Google Cloud Console](https://console.cloud.google.com/).
- Create a new project.
- Navigate to **APIs & Services > Library**, search for "YouTube Data API v3", and enable it.
- Go to **APIs & Services > Credentials**, click **+ CREATE CREDENTIALS**, and choose **API key**.
- Copy the generated API key.

### 3. Set Up Environment Variables

Create a file named `.env` in the root of the project folder.

Add your API key to this file:

```
YOUTUBE_API_KEY="PASTE_YOUR_API_KEY_HERE"
```

### 4. Install Dependencies

Install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 5. Run the Application

Start the Flask development server.

```bash
python api/app.py
```

The application will now be running at `http://127.0.0.1:5000`. Open this URL in your web browser to access the frontend and use the app.

## Deployment to Vercel

This project is configured for easy deployment on Vercel.

### Push to GitHub

Make sure your code, including the `vercel.json` and `requirements.txt` files, is pushed to a GitHub repository. Your `.gitignore` file should prevent the `.env` file from being uploaded.

### Import to Vercel

Log in to Vercel, import your GitHub repository, and Vercel will automatically detect the Python configuration.

### Add Environment Variable

In the project settings on Vercel, navigate to the **Environment Variables** section. Add your API key:

- **Name**: `YOUTUBE_API_KEY`
- **Value**: `PASTE_YOUR_API_KEY_HERE`

### Deploy

Click **Deploy**. Vercel will build and deploy your application.

### Update Frontend URL

After deployment, update the fetch URL in `index.html` to point to your new Vercel app URL.

## Project Structure

```
.
├── .gitignore         # Tells Git which files to ignore
├── README.md          # This file
├── api/
│   └── app.py         # The core Flask backend application
├── index.html         # The frontend UI
├── script.js          # The frontend JavaScript
├── privacy.html       # Privacy Policy page
├── terms.html         # Terms & Conditions page
├── contact.html       # Contact page
├── requirements.txt   # List of Python dependencies
└── vercel.json        # Configuration for Vercel deployment
