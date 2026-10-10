from bridge import ai_transform, app, bridge


def post_to_instagram_reel(video_url, caption):
  print(
      f"🚀 [VIBE DISPATCH] Posting Reel -> URL: {video_url}\n   Caption:"
      f" {caption}"
  )
  return {"status": "success", "platform": "instagram"}


@bridge.connect("youtube_new_video")
def yt_to_ig(data):
  video_url = data.get("url", "https://youtube.com/watch?v=default")
  raw_title = data.get("title", "New drop!")

  # ⚡ ONE-LINE AI MAGIC: Transform raw title into an instant viral hook
  smart_caption = ai_transform(
      raw_title, prompt="Add viral tags and high-energy hooks"
  )

  # Route to output
  res = post_to_instagram_reel(video_url, smart_caption)
  return res


if __name__ == "__main__":
  print("⚡ AI Vibe Middleman running on http://localhost:5000")
  app.run(port=5000, debug=True)