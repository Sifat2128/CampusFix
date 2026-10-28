import os
import json
import re
import socket
from typing import Optional
import httpx
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from app import models
from app.services.chat_tools.tools_spec import TOOLS_DEFINITION
from app.services.chat_tools.dispatcher import dispatch_tool

DEFAULT_SYSTEM_INSTRUCTIONS = (
    "You are the CampusFix AI Assistant for our campus issue tracking platform. "
    "You have access to real-time database tools. Use them whenever the user asks about "
    "campus issues, issue counts, statuses, or historical changes. "
    "Never make up issue IDs, statuses, or statistics. Always rely on tool results. "
    "Be concise, helpful, and friendly."
)

def _is_ollama_port_open(host: str = "127.0.0.1", port: int = 11434, timeout: float = 0.4) -> bool:
    """Fast check to see if Ollama is running locally without freezing the request."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

async def _detect_ollama_model(client: AsyncOpenAI) -> str:
    """Auto-discovers the installed model name from your local Ollama instance."""
    env_model = os.getenv("OLLAMA_MODEL")
    if env_model:
        return env_model
    try:
        models_resp = await client.models.list()
        if models_resp and models_resp.data:
            return models_resp.data[0].id
    except Exception:
        pass
    return "qwen2.5vl-local:latest"


async def _run_tool_calling_loop(client: AsyncOpenAI, model: str, question: str, current_user: models.User, db: Session) -> dict:
    """
    Executes Autonomous LLM Tool Calling:
    - First attempts native API tool calling (OpenAI / Ollama tools parameter).
    - If Ollama model doesn't support the tools parameter (e.g. Vision models like qwen2.5vl),
      seamlessly falls back to prompt-guided JSON tool calling.
    - Zero keyword matching: the model decides everything autonomously.
    """
    role_str = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    system_prompt = (
        f"{DEFAULT_SYSTEM_INSTRUCTIONS}\n"
        f"Active User Context: Name='{current_user.name}', Role='{role_str}'."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    # -------------------------------------------------------------
    # METHOD 1: Native API Tool Calling (OpenAI / Llama 3.2 / Qwen 2.5 Text)
    # -------------------------------------------------------------
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS_DEFINITION,
            tool_choice="auto",
            max_tokens=400,
            temperature=0.2
        )

        response_msg = response.choices[0].message
        tool_calls = response_msg.tool_calls

        # Case A: Model answered directly without needing a tool
        if not tool_calls:
            return {
                "answer": response_msg.content.strip(),
                "tool_used": None
            }

        # Case B: Model selected a database tool!
        messages.append(response_msg)
        executed_tools = []

        for tool_call in tool_calls:
            fn_name = tool_call.function.name
            try:
                fn_args = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError:
                fn_args = {}

            tool_result = dispatch_tool(db=db, current_user=current_user, tool_name=fn_name, arguments=fn_args)
            executed_tools.append(fn_name)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result)
            })

        final_response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=400,
            temperature=0.2
        )

        return {
            "answer": final_response.choices[0].message.content.strip(),
            "tool_used": ", ".join(executed_tools) if executed_tools else None
        }

    except Exception as api_err:
        # Check if the model explicitly does not support the native 'tools' HTTP parameter
        # (Very common for Vision-Language models like qwen2.5vl in Ollama)
        err_msg = str(api_err).lower()
        if "does not support tools" not in err_msg and "invalid_request_error" not in err_msg:
            raise api_err

    # -------------------------------------------------------------
    # METHOD 2: Prompt-Guided Autonomous Tool Calling (For Vision / Custom Models)
    # -------------------------------------------------------------
    tools_desc = json.dumps([t['function'] for t in TOOLS_DEFINITION], indent=2)
    prompt_sys = (
        f"{system_prompt}\n\n"
        "You have access to real-time database tools:\n"
        f"{tools_desc}\n\n"
        "If you need to query the database, you MUST reply ONLY with a JSON object in this format:\n"
        '```json\n{"tool": "function_name", "arguments": {...}}\n```\n'
        "If no tool is needed or after receiving tool results, reply naturally to the user. Never invent fake data."
    )

    t1_messages = [
        {"role": "system", "content": prompt_sys},
        {"role": "user", "content": question}
    ]

    t1_res = await client.chat.completions.create(
        model=model,
        messages=t1_messages,
        temperature=0.1
    )
    t1_out = t1_res.choices[0].message.content.strip()

    # Check if model issued a tool call in JSON format
    match = re.search(r'\{.*"tool"\s*:\s*"([^"]+)".*\}', t1_out, re.DOTALL)
    if match:
        try:
            call_data = json.loads(match.group(0))
            fn_name = call_data.get("tool")
            fn_args = call_data.get("arguments", {})

            tool_result = dispatch_tool(db=db, current_user=current_user, tool_name=fn_name, arguments=fn_args)

            t2_messages = [
                {"role": "system", "content": prompt_sys},
                {"role": "user", "content": question},
                {"role": "assistant", "content": t1_out},
                {
                    "role": "user",
                    "content": f"Database Tool Output for '{fn_name}':\n{json.dumps(tool_result)}\n\nPlease provide a clear, friendly answer to my question based strictly on this real data."
                }
            ]

            t2_res = await client.chat.completions.create(
                model=model,
                messages=t2_messages,
                temperature=0.2
            )
            return {
                "answer": t2_res.choices[0].message.content.strip(),
                "tool_used": fn_name
            }
        except Exception as parse_err:
            print(f"[AI Provider] Error parsing model tool call: {parse_err}")

    # If no tool was requested, the model's answer is already final
    return {
        "answer": t1_out,
        "tool_used": None
    }


async def ask_ai_with_tools(question: str, current_user: models.User, db: Session) -> dict:
    """
    Tiered Agent Execution:
    1. Primary: Cloud OpenAI with Autonomous Tool Calling
    2. Fallback: Local Ollama (supports both text models and vision models like qwen2.5vl)
    3. Offline Notice if neither service is running
    """
    # 1. Primary: Cloud OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key.strip():
        try:
            cloud_client = AsyncOpenAI(api_key=openai_key, timeout=httpx.Timeout(20.0, connect=3.0))
            return await _run_tool_calling_loop(
                client=cloud_client,
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                question=question,
                current_user=current_user,
                db=db
            )
        except Exception as cloud_err:
            print(f"[AI Provider] Cloud OpenAI failed: {cloud_err}. Trying local Ollama...")

    # 2. Fallback: Local Ollama
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    if _is_ollama_port_open():
        try:
            local_client = AsyncOpenAI(
                base_url=ollama_url,
                api_key="ollama",
                timeout=httpx.Timeout(90.0, connect=3.0)
            )
            model_name = await _detect_ollama_model(local_client)
            return await _run_tool_calling_loop(
                client=local_client,
                model=model_name,
                question=question,
                current_user=current_user,
                db=db
            )
        except Exception as local_err:
            print(f"[AI Provider] Local Ollama tool calling error: {local_err}")

    # 3. If neither service is available
    return {
        "answer": (
            "AI service is currently offline. "
            "Please start your local Ollama ('ollama run <model>') or add OPENAI_API_KEY to your .env file."
        ),
        "tool_used": None
    }
