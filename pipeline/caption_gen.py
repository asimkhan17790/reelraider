import logging
import anthropic
import config

logger = logging.getLogger(__name__)

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

_SYSTEM = (
    "You are a YouTube short-form content specialist. "
    "Write engaging, SEO-optimised metadata for viral clips. "
    "Always be concise and use relevant trending hashtags."
)


def generate_caption(video: dict) -> dict:
    video_id = video["video_id"]
    logger.debug("generate_caption: video_id=%s title=%r", video_id, video.get("title"))
    logger.info("Generating caption for video_id=%s", video_id)

    prompt = f"""Given this YouTube video metadata, write short-form clip metadata.

<user_content>
Original title: {video['title']}
Original description: {video['description'][:500]}
Original channel: {video['channel']}
Original URL: {video['url']}
</user_content>

Return EXACTLY in this format (no extra text):
TITLE: <punchy title max 60 chars>
DESCRIPTION: <150 words max, end with 3 hashtags, include "Original: {video['url']}">
TAGS: <5 comma-separated SEO tags>"""

    response = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=[{
            "type": "text",
            "text": _SYSTEM,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text
    logger.debug(
        "Claude API response: video_id=%s input_tokens=%d output_tokens=%d",
        video_id,
        response.usage.input_tokens,
        response.usage.output_tokens,
    )
    result = {"title": video["title"], "description": "", "tags": []}

    for line in text.splitlines():
        if line.startswith("TITLE:"):
            result["title"] = line.removeprefix("TITLE:").strip()
        elif line.startswith("DESCRIPTION:"):
            result["description"] = line.removeprefix("DESCRIPTION:").strip()
        elif line.startswith("TAGS:"):
            result["tags"] = [t.strip() for t in line.removeprefix("TAGS:").split(",")]

    logger.info(
        "Caption generated: video_id=%s title=%r tags=%s",
        video_id,
        result["title"],
        result["tags"],
    )
    return result
