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
                    "role": "system",
                    "content": "пиши без гласных букв"
                },
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