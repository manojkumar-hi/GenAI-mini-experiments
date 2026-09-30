import json
from typing import List, Dict, Any
from groq import Groq
from tools import get_current_time, get_weather, tool_schemas

class AgentActionRequest:
    """Provider-independent internal representation for an action request."""
    def __init__(self, action: str, parameters: Dict[str, Any], request_id: str):
        self.action = action
        self.parameters = parameters
        self.request_id = request_id

    def __repr__(self):
        return f"AgentActionRequest(action={self.action}, parameters={self.parameters}, request_id={self.request_id})"


class AgentRuntime:
    def __init__(self, client: Groq, model: str = "openai/gpt-oss-120b"):
        self.client = client
        self.model = model

    def run(self, messages: List[Dict]) -> str:
        """Runs the agent loop with tool calling support."""
        MAX_ITERATIONS = 5
        for _ in range(MAX_ITERATIONS):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tool_schemas,
                tool_choice="auto",
                max_tokens=500,
                temperature=0.6,
            )
            
            message = response.choices[0].message
            
            # If the model wants to call tools
            if message.tool_calls:
                # Append the model's message as a dictionary
                assistant_msg = {
                    "role": "assistant",
                    "content": message.content
                }
                if message.tool_calls:
                    assistant_msg["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                messages.append(assistant_msg)
                
                for tool_call in message.tool_calls:
                    # Parse arguments safely
                    try:
                        parameters = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        parameters = {}
                        
                    # 1. Convert Groq-specific tool call to internal AgentActionRequest
                    action_req = AgentActionRequest(
                        action=tool_call.function.name,
                        parameters=parameters,
                        request_id=tool_call.id
                    )
                    
                    # 2. Execute the tool using the internal representation
                    result = self.execute_tool(action_req)
                    
                    # 3. Append the result to the conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": action_req.request_id,
                        "name": action_req.action,
                        "content": str(result)
                    })
            else:
                # If no tools were called, return the final response
                return message.content
        
        return "Max iterations reached while trying to resolve the request."

    def execute_tool(self, action_req: AgentActionRequest) -> Any:
        """Executes a given tool based on AgentActionRequest."""
        if action_req.action == "get_current_time":
            return get_current_time(**action_req.parameters)
        elif action_req.action == "get_weather":
            return get_weather(**action_req.parameters)
        return f"Error: Unknown tool {action_req.action}"
