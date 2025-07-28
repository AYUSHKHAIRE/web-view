import sys
import os
import asyncio
from dotenv import load_dotenv
from browser_use.llm import ChatGoogle
from browser_use import Agent

async def run_agent(user_id, question, BASE_DIR):
    load_dotenv("chrome/.env")

    def extract_final_result(agent_tuple):
        if not isinstance(agent_tuple, tuple) or len(agent_tuple) != 2:
            print("Invalid input format")
            return None

        history_key, history_list = agent_tuple
        if history_key != "history" or not isinstance(history_list, list):
            print("Invalid history structure")
            return None

        for step in reversed(history_list):  # Reverse to get the last step first
            if hasattr(step, "result") and isinstance(step.result, list):
                for result in step.result:
                    if getattr(result, "is_done", False):
                        # Found the final result step
                        final_text = getattr(result, "extracted_content", None)
                        if final_text:
                            return final_text
                        long_term = getattr(result, "long_term_memory", None)
                        if long_term:
                            return long_term
        return "No final result found"

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in .env", flush=True)
        return

    llm = ChatGoogle(model='gemini-2.0-flash', api_key=api_key)
    agent = Agent(task=question, llm=llm, return_steps=True)

    output_path = os.path.join(BASE_DIR, "browse/agent/user_logs", f"{user_id}.log")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        steps = await agent.run()
        for step in steps:
            if isinstance(step, dict):
                line = step.get("log") or step.get("observation") or ""
                if line:
                    print(line, flush=True)  # flush to make sure line shows up immediately
                    with open(output_path, "a", encoding="utf-8") as f:
                        f.write(line + "\n")

                if step.get("status") == "finished":
                    result = step.get("result")
                    final_line = f"[FINAL OUTPUT] {result}"
                    print("=" * 55, flush=True)
                    print(final_line, flush=True)
                    print("=" * 55, flush=True)
                    with open(output_path, "a", encoding="utf-8") as f:
                        f.write(final_line + "\n")
                    break
            elif isinstance(step, tuple):
                print("==========================")
                final_touple = extract_final_result(step)
                print(final_touple)
                print("==========================")
            else:
                print("got something else ...", step, flush=True)

    except Exception as e:
        print(f"[ERROR] Agent execution failed: {e}", flush=True)

def main():
    if len(sys.argv) != 4:
        print("Usage: python agent_executor.py <user_id> <question> <BASE_DIR>", flush=True)
        sys.exit(1)

    user_id = sys.argv[1]
    question = sys.argv[2]
    BASE_DIR = sys.argv[3]
    asyncio.run(run_agent(user_id, question, BASE_DIR))

if __name__ == "__main__":
    main()
