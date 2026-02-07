from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

# First API call with reasoning
response = client.chat.completions.create(
    model="stepfun/step-3.5-flash:free",
    messages=[
                {
                    "role": "user",
                    "content": "напиши стих про осень и березу"
                }
            ],
    extra_body={"reasoning": {"enabled": True}}
)

# Extract the assistant message with reasoning_details
response = response.choices[0].message
print(response.content)  # Assistant's response
"""
# Preserve the assistant message with reasoning_details
messages = [
  {"role": "user", "content": "How many r's are in the word 'strawberry'?"},
  {
    "role": "assistant",
    "content": response.content,
    "reasoning_details": response.reasoning_details  # Pass back unmodified
  },
  {"role": "user", "content": "Are you sure? Think carefully."}
]

# Second API call - model continues reasoning from where it left off
response2 = client.chat.completions.create(
  model="stepfun/step-3.5-flash:free",
  messages=messages,
  extra_body={"reasoning": {"enabled": True}}
)
"""