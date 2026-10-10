from bridge import app, bridge


# Mock action helper (we'll make this talk to real APIs soon)
def post_to_instagram_reel(video_url, caption):
  print(f"🚀 [VIBE MATCH] Dispatching Reel -> URL: {video_url} | Caption: {caption}")
  return {"status": "success", "platform": "instagram"}


# Wire YouTube -> Instagram together
@bridge.connect("youtube_new_video")
def yt_to_ig(data):
  video_url = data.get("url", "https://youtube.com/watch?v=default")
  title = data.get("title", "New drop!")

  # Transform data on the fly
  vibe_caption = f"🔥 NEW DROP: {title} #vibes #content"

  # Trigger the output
  res = post_to_instagram_reel(video_url, vibe_caption)
  return res


if __name__ == "__main__":
  print("⚡ Vibe Middleman is alive on http://localhost:5000")
  app.run(port=5000, debug=True)