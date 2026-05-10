from typing import Dict, Any
from app.agents.llm_client import generate_completion
import json

class BaseAgent:
    def __init__(self, department_id: str, department_name: str, role_description: str):
        self.department_id = department_id
        self.department_name = department_name
        self.role_description = role_description
        
    def analyze(self, ticket_data: Dict[str, Any], customer_data: Dict[str, Any], event_details: str) -> Dict[str, Any]:
        """
        Runs the analysis for this department.
        Returns a dictionary with analysis and proposed action.
        """
        system_prompt = f"""
        You are an expert analyst in the {self.department_name} department at STB Bank.
        Your role is: {self.role_description}.
        Provide your analysis in a structured JSON format with the following keys:
        - "analysis": A clear, concise explanation of the situation from your department's perspective.
        - "proposed_action": The specific action your department recommends.
        - "confidence": A percentage (e.g., "90%") indicating your confidence.
        Output ONLY valid JSON.
        """
        
        prompt = f"""
        Ticket ID: {ticket_data.get('id', 'Unknown')}
        Customer Segment: {customer_data.get('segment', 'Unknown')}
        Loan Size: {customer_data.get('loan_size', 'Unknown')}
        Risk Stage: {customer_data.get('risk_stage', 'Unknown')}
        
        Event Details:
        {event_details}
        
        Analyze this event based on your role and propose an action.
        """
        
        result_text = generate_completion(prompt=prompt, system_prompt=system_prompt)
        
        try:
            # Try to parse the output as JSON
            # Extract JSON substring by finding the first '{' and last '}'
            clean_text = result_text.strip()
            start_idx = clean_text.find('{')
            end_idx = clean_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = clean_text[start_idx:end_idx+1]
                parsed_result = json.loads(json_str)
                return parsed_result
            else:
                raise ValueError("No JSON object found in response.")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to parse JSON from LLM: {e}. Raw: {result_text}")
            return {
                "analysis": "Failed to generate structured analysis. Raw output: " + result_text[:200],
                "proposed_action": "Manual review required",
                "confidence": "0%"
            }
