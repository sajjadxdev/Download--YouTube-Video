from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import yt_dlp
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for flashing error messages

# Define the folder to store downloaded videos
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url_link = request.form.get('url_link')
    format_choice = request.form.get('format')
    
    if not url_link:
        flash("Please enter a URL.")
        return redirect(url_for('index'))

    try:
        # Configure yt-dlp based on selected format
        if format_choice == 'mp3':
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),  # Save file with title in the 'downloads' folder
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:  # Default to mp4
            ydl_opts = {
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),  # Save file with title in the 'downloads' folder
                'format': 'best',
            }
        
        # Use yt-dlp to download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Attempting to download...")
            info_dict = ydl.extract_info(url_link, download=True)  # This will download the video or audio
            print("Download complete.")
            video_title = info_dict.get('title', None)
            file_extension = info_dict.get('ext', 'mp4')  # Default to mp4 if not specified
            video_file = f"{video_title}.{file_extension}"
            download_path = os.path.join(DOWNLOAD_FOLDER, video_file)

            # Verify the downloaded file exists
            if not os.path.isfile(download_path):
                raise FileNotFoundError("The downloaded file was not found.")

        # Video download information to display
        result = {
            'Video Title': video_title,
            'File Name': video_file,
            'File Path': download_path,
            'Format': format_choice  # Added format to the result
        }
        
        # Render the result page with the download details
        return render_template('result.html', result=result)

    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        print(f"Error: {str(e)}")  # Print the error for debugging
        return redirect(url_for('index'))

@app.route('/download_file/<path:filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)
    except Exception as e:
        flash(f"File not found: {str(e)}")
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
