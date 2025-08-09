from pyrit.common import IN_MEMORY, initialize_pyrit
from pyrit.orchestrator import PromptSendingOrchestrator
from pyrit.prompt_target.http_target.http_target import (
  HTTPTarget,
)
from pyrit.prompt_target import (
    get_http_target_json_response_callback_function,
    get_http_target_regex_matching_callback_function,
)


initialize_pyrit(memory_db_type=IN_MEMORY)
url = "http://localhost:11434/api/chat"
api_key = "test"

raw_http_request = f"""
    POST {url} HTTP/1.1
    Content-Type: application/json
    api-key: {api_key}

    {{
        "model": "llama3",
        "messages": [
            {{"role": "user", "content": {{PROMPT}} }}
        ],
        "max_tokens": 50,
        "temperature": 0.2,
        "stream": False
    }}
"""

# test_prompt = "TEST-PROMPT-HERE"
# # Manually replace the placeholder with the test prompt
# test_http_request = raw_http_request.replace("{PROMPT}", test_prompt)
# print(test_http_request)

# print(raw_http_request)

parsing_fn_chat = get_http_target_json_response_callback_function(key="message.content")

http_target = HTTPTarget(
  http_request=raw_http_request,
  prompt_regex_string="{PROMPT}",   # literal substring to replace
  callback_function=parsing_fn_chat,
  use_tls= False
)

orchestrator = PromptSendingOrchestrator(objective_target=http_target)

# right before you call send_prompts_async:
# print("---- outgoing HTTP ----")
# print(await http_target._inject_prompt("TEST-PROMPT-HERE"))
print("-----------------------")


import asyncio

async def main():
    responses = await orchestrator.send_prompts_async(
      prompt_list=[
        "How do I bake a cake?",
        "Tell me about the French Revolution",
      ]
    )
    for r in responses:
        print(r.generated_text)

asyncio.run(main())
