from bridge import ai_transform, app, bridge


def post_to_instagram_reel(video_url, caption):
  print(f"\n🚀 [AUTOMATED DISPATCH] Posting Reel -> URL: {video_url}")
  print(f"📝 AI Caption saved to Database:\n{caption}\n")
  return {"status": "success", "platform": "instagram"}


@bridge.connect("youtube_new_video")
def yt_to_ig(data):
  video_url = data.get("url", "")
  raw_title = data.get("title", "")

  # Run local Ollama transformation and pass the event name for logging
  smart_caption = ai_transform(
      raw_title,
      prompt="Write a viral high-energy hook for Instagram Reels",
      trigger_name="youtube_new_video",
  )

  return post_to_instagram_reel(video_url, smart_caption)


if __name__ == "__main__":
  GOOGLE_CHANNEL_ID = "UCK8sQmJBp8GCxrOtXWBpyEA"
  bridge.start_youtube_listener(
      channel_id=GOOGLE_CHANNEL_ID,
      trigger_event="youtube_new_video",
      interval_seconds=10,
  )

  print("⚡ Persistent Middleman running on http://localhost:5000")
  app.run(port=5000, debug=True)