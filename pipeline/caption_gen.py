import anthropic
import config

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

_SYSTEM = (
    "You are a YouTube short-form content specialist. "
    "Write engaging, SEO-optimised metadata for viral clips. "
    "Always be concise and use relevant trending hashtags."
)


def generate_caption(video: dict) -> dict:
    prompt = f"""Given this YouTube video metadata, write short-form clip metadata.

Original title: {video['title']}
Original description: {video['description'][:500]}
Original channel: {video['channel']}
Original URL: {video['url']}

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
    result = {"title": video["title"], "description": "", "tags": []}

    for line in text.splitlines():
        if line.startswith("TITLE:"):
            result["title"] = line.removeprefix("TITLE:").strip()
        elif line.startswith("DESCRIPTION:"):
            result["description"] = line.removeprefix("DESCRIPTION:").strip()
        elif line.startswith("TAGS:"):
            result["tags"] = [t.strip() for t in line.removeprefix("TAGS:").split(",")]

    return result
