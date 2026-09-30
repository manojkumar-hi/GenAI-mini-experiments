import unittest
from unittest.mock import MagicMock
from agent import AgentRuntime, AgentActionRequest
from tools import get_current_time, get_weather, tool_schemas
import json
import datetime
from unittest.mock import patch, MagicMock

class TestAgent(unittest.TestCase):
    def test_tool_schema(self):
        """Test that the tool schema is correctly defined."""
        self.assertIsInstance(tool_schemas, list)
        self.assertTrue(len(tool_schemas) > 0)
        tool = tool_schemas[0]
        self.assertEqual(tool["type"], "function")
        self.assertEqual(tool["function"]["name"], "get_current_time")
        self.assertIn("timezone", tool["function"]["parameters"]["properties"])

    def test_tool_execution(self):
        """Test the local tool execution."""
        # Execute without tz
        time_str = get_current_time()
        self.assertIsInstance(time_str, str)
        # Should be able to parse it (YYYY-MM-DD HH:MM:SS TZ)
        self.assertTrue("UTC" in time_str)
        
        # Execute with specific tz
        time_str_est = get_current_time("America/New_York")
        self.assertTrue("EDT" in time_str_est or "EST" in time_str_est)

    @patch('tools.urllib.request.urlopen')
    def test_get_weather(self, mock_urlopen):
        """Test getting weather with a mocked API."""
        # Mock geocoding response
        mock_geo_resp = MagicMock()
        mock_geo_resp.read.return_value = json.dumps({
            "results": [{"name": "Visakhapatnam", "latitude": 17.68, "longitude": 83.21}]
        }).encode('utf-8')
        mock_geo_resp.__enter__.return_value = mock_geo_resp
        
        # Mock weather response
        mock_weather_resp = MagicMock()
        mock_weather_resp.read.return_value = json.dumps({
            "current_weather": {"temperature": 32.5, "windspeed": 12.0}
        }).encode('utf-8')
        mock_weather_resp.__enter__.return_value = mock_weather_resp
        
        # Configure side effect for successive urlopen calls
        mock_urlopen.side_effect = [mock_geo_resp, mock_weather_resp]
        
        result = get_weather("Visakhapatnam")
        self.assertIn("Visakhapatnam", result)
        self.assertIn("32.5", result)
        self.assertIn("12.0", result)
        
        # Test error handling (e.g. location not found)
        mock_geo_empty = MagicMock()
        mock_geo_empty.read.return_value = json.dumps({}).encode('utf-8')
        mock_geo_empty.__enter__.return_value = mock_geo_empty
        mock_urlopen.side_effect = [mock_geo_empty]
        result_error = get_weather("UnknownCityXYZ")
        self.assertIn("Error: Could not find location", result_error)

    def test_agent_action_request_conversion(self):
        """Test conversion to internal AgentActionRequest."""
        req = AgentActionRequest("get_current_time", {"timezone": "UTC"}, "req_123")
        self.assertEqual(req.action, "get_current_time")
        self.assertEqual(req.parameters["timezone"], "UTC")
        self.assertEqual(req.request_id, "req_123")
        
        # Test execute_tool method
        mock_client = MagicMock()
        runtime = AgentRuntime(mock_client)
        result = runtime.execute_tool(req)
        self.assertIsInstance(result, str)
        self.assertTrue("UTC" in result)

    def test_normal_text_response(self):
        """Test agent runtime for a normal text response (no tools)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_message = MagicMock()
        
        mock_message.content = "Hello there!"
        mock_message.tool_calls = None
        mock_response.choices = [MagicMock(message=mock_message)]
        
        mock_client.chat.completions.create.return_value = mock_response
        
        runtime = AgentRuntime(mock_client)
        messages = [{"role": "user", "content": "Hi"}]
        
        result = runtime.run(messages)
        self.assertEqual(result, "Hello there!")
        
        # verify tools were passed to groq
        mock_client.chat.completions.create.assert_called_once()
        kwargs = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(kwargs["tools"], tool_schemas)

    def test_tool_call_iterations(self):
        """Test agent runtime for tool-call loop."""
        mock_client = MagicMock()
        
        # First response: tool call
        mock_message_1 = MagicMock()
        mock_message_1.content = None
        
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "get_current_time"
        mock_tool_call.function.arguments = json.dumps({"timezone": "UTC"})
        mock_message_1.tool_calls = [mock_tool_call]
        
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock(message=mock_message_1)]
        
        # Second response: text
        mock_message_2 = MagicMock()
        mock_message_2.content = "The time is now."
        mock_message_2.tool_calls = None
        
        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock(message=mock_message_2)]
        
        # Set side effect to return sequence of responses
        mock_client.chat.completions.create.side_effect = [mock_response_1, mock_response_2]
        
        runtime = AgentRuntime(mock_client)
        messages = [{"role": "user", "content": "What time is it?"}]
        
        result = runtime.run(messages)
        self.assertEqual(result, "The time is now.")
        
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        # Check that the tool response was appended to messages
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]["role"], "user")
        # messages[1] is mock_message_1
        self.assertEqual(messages[2]["role"], "tool")
        self.assertEqual(messages[2]["tool_call_id"], "call_123")
        self.assertEqual(messages[2]["name"], "get_current_time")
        # messages[3] is not there, because the loop just returns the text content of the second message and does not append it to `messages` unless we did it manually. The `run` method just returns `message.content`.

if __name__ == '__main__':
    unittest.main()
