import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="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",
)

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=8192,
    temperature=0,
    system="system prompt here ",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "text goes here"
                }
            ]
        }
    ]
)
print(message.content[0].text.strip())

