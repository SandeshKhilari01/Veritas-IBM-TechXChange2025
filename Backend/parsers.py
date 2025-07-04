"""
Custom output parsers for the Compliance RAG Agent
"""

import json
import re
from langchain_core.output_parsers import BaseOutputParser


class CustomAgentOutputParser(BaseOutputParser):
    """Custom output parser that can handle various LLM output formats."""
    
    def parse(self, text: str):
        """Parse the LLM output to extract action and action_input."""
        try:
            # Try to find JSON in the text
            json_match = re.search(r'\{[^{}]*"action"[^{}]*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                return parsed
            
            # If no JSON found, try to extract action from text
            if "Final Answer" in text:
                # Extract the final answer
                final_answer_match = re.search(r'Final Answer[:\s]*(.+)', text, re.DOTALL)
                if final_answer_match:
                    answer = final_answer_match.group(1).strip()
                    return {
                        "action": "Final Answer",
                        "action_input": answer
                    }
            
            # Fallback: return a default response
            return {
                "action": "Final Answer",
                "action_input": "I understand your request. Please proceed with the next step."
            }
            
        except Exception as e:
            # If all parsing fails, return a default response
            return {
                "action": "Final Answer",
                "action_input": f"Parsing error occurred: {str(e)}. Please try again."
            }
