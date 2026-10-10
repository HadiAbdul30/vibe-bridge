from bridge import ai_transform, app, bridge


def post_to_instagram_reel(video_url, caption):
  print(f"\n🚀 [DISPATCH -> INSTAGRAM] Posting Reel -> URL: {video_url}")
  print(f"📝 Caption:\n{caption}\n")
  return {"status": "success", "platform": "instagram"}


def post_to_discord_channel(video_url, caption):
  print(f"\n💬 [DISPATCH -> DISCORD] Sending Announcement -> URL: {video_url}")
  print(f"📢 Message:\n{caption}\n")
  return {"status": "success", "platform": "discord"}


@bridge.connect("youtube_new_video")
def yt_multichannel_fanout(data):
  video_url = data.get("url", "")
  raw_title = data.get("title", "")

  # Run local Ollama transformation once
  smart_caption = ai_transform(
      raw_title,
      prompt=(
          "Write a punchy, high-energy 1-sentence social media announcement with"
          " emojis"
      ),
      trigger_name="youtube_new_video_fanout",
  )

  # Fan out to multiple destinations!
  ig_result = post_to_instagram_reel(video_url, smart_caption)
  discord_result = post_to_discord_channel(
      video_url, f"🚨 New video dropped! {smart_caption}"
  )

  return {
      "fanout": "success",
      "destinations": [ig_result["platform"], discord_result["platform"]],
  }


if __name__ == "__main__":
  GOOGLE_CHANNEL_ID = "UCK8sQmJBp8GCxrOtXWBpyEA"
  bridge.start_youtube_listener(
      channel_id=GOOGLE_CHANNEL_ID,
      trigger_event="youtube_new_video",
      interval_seconds=10,
  )

  print("⚡ Multichannel Fanout Middleman running on http://localhost:5000")
  app.run(port=5000, debug=True)