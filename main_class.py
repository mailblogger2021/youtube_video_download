import tkinter as tk
from tkinter import ttk, filedialog
from threading import Thread
import os
import yt_dlp
import subprocess
import logging
import json
import requests

# logging.basicConfig(filename="results/main.log",level=logging.DEBUG)
# logging.debug("This is debugging message")
# logging.info("This is Info message")
# logging.warning("This is warning message")


class download_youtube_video:

    def __init__(self, save_path: str = "artifacts/videos"):
        self.save_path = save_path
        self.create_directory(self.save_path)

    def create_directory(self, path) -> None:
        os.makedirs(name=path, exist_ok=True)

    def get_short_links(self, channel_url):
        ydl_opts = {
            "quiet": True,
            "extract_flat": True,
            "playlist_end": 100,
        }

        if "/@" in channel_url:

            channel_username = channel_url.split("/@")[1].split("/")[0]

            channel_url = f"https://www.youtube.com/@{channel_username}/shorts"
        else:

            channel_url = channel_url.split("/about")[0]
            channel_url = channel_url.split("/community")[0]
            channel_url = channel_url.split("/playlist")[0]
            channel_url = channel_url.split("/playlists")[0]
            channel_url = channel_url.split("/streams")[0]
            channel_url = channel_url.split("/featured")[0]
            channel_url = channel_url.split("/videos")[0]

            channel_url += "/shorts"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(channel_url, download=False)
            if "entries" in result:
                video_ids = [entry["id"] for entry in result["entries"]]
                short_links = [
                    f"https://www.youtube.com/shorts/{video_id}"
                    for video_id in video_ids
                ]
                self.short_links = short_links
                return short_links
            else:
                print("No videos found on the channel.")
                return []

    def download_videos_from_links(self, links, output_path):
        total_links = len(links)
        for index, link in enumerate(links, start=1):
            link = link.strip()
            print("Started Index - ", index, " Link - ", link)
            # try:
            subprocess.run(
                [
                    "yt-dlp",
                    "--geo-bypass",
                    "--geo-bypass-country",
                    "IN",  # Simulate access from India
                    "--proxy",
                    "http://123.45.67.89:8080",  # Replace with your valid proxy
                    "--quiet",
                    "--retry",
                    "3",  # Retry 3 times in case of failure
                    "-f",
                    "bestvideo+bestaudio/best",  # Best video and audio quality
                    "--merge-output-format",
                    "mp4",  # Merge output as MP4
                    "--output",
                    os.path.join(output_path, "%(title)s.%(ext)s"),
                    link,
                ],
                check=True,
            )
            # subprocess.run(['yt-dlp', '--quiet', '--output', os.path.join(output_path, '%(title)s.%(ext)s'), link], check=True)
            # except subprocess.CalledProcessError as e:
            #     print(f"Error downloading {link}: {e}")
            # finally:
            #     # progress_var.set(int((index / total_links) * 100))
            #     print("Completed Index - ", index, " Link - ", link)

    def download_youtube_short(self, video_url, save_path="artifacts"):
        # Ensure the save_path exists
        os.makedirs(name=save_path, exist_ok=True)

        ydl_opts = {
            "outtmpl": f"{save_path}/1.%(title)s.%(ext)s",  # Video file save path
            "format": "bestvideo+bestaudio/best",  # Best video and audio
            "merge_output_format": "mp4",  # Output format
            "writeinfojson": True,  # Save metadata JSON
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Download video and metadata
                info_dict = ydl.extract_info(video_url, download=True)

                # Extract metadata
                video_title = info_dict.get("title", "unknown_title")
                video_description = info_dict.get(
                    "description", "No description available."
                )
                video_tags = info_dict.get("tags", [])

                # Save description and tags to text files
                description_path = os.path.join(
                    save_path, f"{video_title}_description.txt"
                )
                with open(description_path, "w", encoding="utf-8") as desc_file:
                    desc_file.write(video_description)

                tags_path = os.path.join(save_path, f"{video_title}_tags.txt")
                with open(tags_path, "w", encoding="utf-8") as tags_file:
                    tags_file.write(", ".join(video_tags))

                print(f"Downloaded video: {video_title}")
                print(f"Description saved to: {description_path}")
                print(f"Tags saved to: {tags_path}")
        except Exception as e:
            print(f"Error: {e}")


def get_location_info():
    try:
        response = requests.get("https://ipinfo.io/json")
        if response.status_code == 200:
            data = response.json()
            country = data.get("country", "Unknown")
            region = data.get("region", "Unknown")
            city = data.get("city", "Unknown")
            loc = data.get("loc", "Unknown")  # Latitude and Longitude
            print(f"Country: {country}")
            print(f"Region: {region}")
            print(f"City: {city}")
            print(f"Location (Lat, Long): {loc}")
        else:
            print(f"Failed to get location info. Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching location info: {e}")


# Call the function
get_location_info()

if __name__ == "__main__":
    # pass
    obj = download_youtube_video()
    short_url = "https://www.youtube.com/shorts/r0wdx3HBxMk"
    obj.download_youtube_short(short_url)

    # youtube_channel_link = "https://www.youtube.com/@CortexTide"
    # short_links = obj.get_short_links(youtube_channel_link)
    # obj.download_videos_from_links(short_links, obj.save_path)
