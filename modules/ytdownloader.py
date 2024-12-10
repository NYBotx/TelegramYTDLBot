import os
import requests
from y2mate_api import Handler
import pytube

# Download the YouTube Video
def download(bot, message, userInput, videoURL):
    try:
        # Initialize the API and YouTube object
        api = Handler(videoURL)
        yt = pytube.YouTube(videoURL)

        mediaPath = f"{os.getcwd()}/vids"

        # Create media path if it doesn't exist
        if not os.path.exists(mediaPath):
            os.makedirs(mediaPath)

        downloadMsg = bot.send_message(chat_id=message.chat.id, text="<b>Downloading...📥</b>")

        # Get the video metadata for the requested quality
        for video_metadata in api.run(quality=userInput):
            vidFileName = f"{video_metadata['vid']}_{video_metadata['q']}.{video_metadata['ftype']}"

            # Download the video
            try:
                # Download video using y2mate API
                api.save(third_dict=video_metadata, dir="vids", naming_format=vidFileName, progress_bar=True)
            except Exception as e:
                bot.reply_to(message, f"Error downloading video: {e}")
                bot.delete_message(chat_id=downloadMsg.chat.id, message_id=downloadMsg.message_id)
                return

            # Once download is complete, edit the message for upload
            bot.edit_message_text(chat_id=downloadMsg.chat.id, message_id=downloadMsg.message_id, text="<b>Uploading...📤</b>")

            # Upload the video to Telegram
            try:
                print(f"Uploading {vidFileName}...")

                thumb = requests.get(yt.thumbnail_url).content  # Fetch thumbnail
                bot.send_video(
                    message.chat.id,
                    open(f"vids/{vidFileName}", 'rb'),
                    thumb=thumb,
                    width=1920,
                    height=1080,
                    caption=f"""
                    <b>Title:</b><i> {yt.title} </i>
                    <b>URL:</b><i> {videoURL} </i>
                    <b>Quality:</b><i> {video_metadata['q']} </i>

                    <i><b>Thanks for Using @{bot.get_me().username}.</b></i>"""
                )

                print(f"File {vidFileName} uploaded successfully.")
            except Exception as e:
                bot.reply_to(message, f"Error uploading video: {e}")
                print(f"Error uploading {vidFileName}: {e}")
                bot.delete_message(chat_id=downloadMsg.chat.id, message_id=downloadMsg.message_id)
                return

            # Cleanup - remove video file after upload
            os.remove(f"{mediaPath}/{vidFileName}")
            print(f"File {vidFileName} removed after upload.")

        # Delete the message showing download progress
        bot.delete_message(chat_id=downloadMsg.chat.id, message_id=downloadMsg.message_id)

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")
        print(f"Error: {e}")
                
