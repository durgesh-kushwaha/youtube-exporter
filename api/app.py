import os
import re
from flask import Flask, request, jsonify, send_file
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import pandas as pd
from io import BytesIO
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def extract_playlist_id(url):
    regex = r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/playlist\?list=([a-zA-Z0-9_-]+)'
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

def parse_iso8601_duration(duration):
    if not duration or 'D' in duration:
        return 'N/A'
        
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if not match:
        return '00:00'
    
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    m, s = divmod(total_seconds, 60)
    h, m = divmod(m, 60)
    
    if h > 0:
        return f"{h:d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"

@app.route('/api/export', methods=['POST'])
def export_playlist():
    if not API_KEY:
        return jsonify({'error': 'Server configuration error: YOUTUBE_API_KEY is not set.'}), 500

    playlist_url = request.json.get('playlist_url')
    if not playlist_url:
        return jsonify({'error': 'Playlist URL is required.'}), 400

    playlist_id = extract_playlist_id(playlist_url)
    if not playlist_id:
        return jsonify({'error': 'Invalid YouTube Playlist URL.'}), 400

    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

        playlist_request = youtube.playlists().list(
            part='snippet',
            id=playlist_id
        )
        playlist_response = playlist_request.execute()
        
        if not playlist_response['items']:
            return jsonify({'error': 'Playlist not found or is private.'}), 404
            
        playlist_title = playlist_response['items'][0]['snippet']['title']
        safe_playlist_title = re.sub(r'[\\/*?:"<>|]', "", playlist_title)
        filename = f"{safe_playlist_title}.csv"

        playlist_items = []
        next_page_token = None

        while True:
            request_playlist_items = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request_playlist_items.execute()

            playlist_items.extend(response['items'])
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        
        video_ids = [
            item['snippet']['resourceId']['videoId'] 
            for item in playlist_items 
            if item.get('snippet', {}).get('resourceId', {}).get('kind') == 'youtube#video'
        ]

        video_details_map = {}
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]
            video_request = youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=",".join(batch_ids)
            )
            video_response = video_request.execute()
            for item in video_response['items']:
                video_details_map[item['id']] = item

        final_video_list = []
        for item in playlist_items:
            video_id = item.get('snippet', {}).get('resourceId', {}).get('videoId')
            if not video_id:
                continue

            video_info = video_details_map.get(video_id)
            if not video_info:
                snippet = item.get('snippet', {})
                final_video_list.append({
                    'Title': snippet.get('title', 'Video Not Available'),
                    'Channel': snippet.get('videoOwnerChannelTitle', 'N/A'),
                    'Published Date': snippet.get('publishedAt', 'N/A').split('T')[0],
                    'URL': f"https://www.youtube.com/watch?v={video_id}",
                    'Views': 'N/A',
                    'Likes': 'N/A',
                    'Duration': 'N/A'
                })
                continue

            snippet = video_info.get('snippet', {})
            stats = video_info.get('statistics', {})
            content_details = video_info.get('contentDetails', {})
            
            final_video_list.append({
                'Title': snippet.get('title', 'N/A'),
                'Channel': snippet.get('channelTitle', 'N/A'),
                'Published Date': snippet.get('publishedAt', 'N/A').split('T')[0],
                'Views': int(stats.get('viewCount', 0)),
                'Likes': int(stats.get('likeCount', 0)),
                'Duration': parse_iso8601_duration(content_details.get('duration', '')),
                'URL': f"https://www.youtube.com/watch?v={video_id}",
            })
            
        df = pd.DataFrame(final_video_list)

        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)

        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename 
        )

    except HttpError as e:
        error_details = e.error_details[0] if e.error_details else {}
        reason = error_details.get('reason', 'unknown')
        print(f"A Google API error occurred: {reason}")
        return jsonify({'error': f'YouTube API Error: {reason}. Check your API key quota and permissions.'}), e.resp.status
    
    except Exception as e:
        print(f"An internal error occurred: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@app.route('/')
def index():
    return send_file(os.path.join(BASE_DIR, 'index.html'))

@app.route('/script.js')
def script():
    return send_file(os.path.join(BASE_DIR, 'script.js'))

@app.route('/privacy.html')
def privacy():
    return send_file(os.path.join(BASE_DIR, 'privacy.html'))

@app.route('/terms.html')
def terms():
    return send_file(os.path.join(BASE_DIR, 'terms.html'))

@app.route('/contact.html')
def contact():
    return send_file(os.path.join(BASE_DIR, 'contact.html'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

