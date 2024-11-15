import os
import re
import json
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, ValidationError

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", openai_api_key=openai_api_key)

# Request Data Model
class BetRequest(BaseModel):
    description: str  # Bet description (e.g., "Will Bitcoin rise above $40,000?")

# Define data models for step outputs using pydantic
class StepOutput(BaseModel):
    has_due_date: bool = None
    has_two_outcomes: bool = None
    is_verifiable: bool = None
    result: str = None

# Generate Workflow
def generate_workflow(description: str):
    """
    Generate a workflow for analyzing the market description using LLM.

    Args:
        description (str): The market description.

    Returns:
        dict: Workflow structure.
    """
    workflow_prompt = f"""
Please generate a step-by-step workflow for analyzing how to validate a market:

Description: "{description}"

Requirements:
- The workflow should contain the following mandatory steps:
  1) "Check for Due Date": Check if the market description has a due date.
  2) "Check for Two Outcomes": Check if the market is binary (only two outcomes).
  3) "Determine Verifiability": Determine if the market is verifiable.
- The workflow must also include at least 2 additional steps relevant to market analysis.
- Each step should be unique and relevant to the analysis of the market.
- The total number of steps must be at least 5.

The workflow should be JSON-formatted with:
- "workflow_name": The name of the workflow.
- "steps": A list of steps, each with:
    - "id": A unique identifier for the step.
    - "label": A short description of the step.
    - "type": The type of the step (e.g., "task", "decision").
    - "input": The expected input for this step.
    - "output": The expected output for this step.
    - "dependencies": A list of step IDs this step depends on.
"""

    # Generate workflow using LLM
    response = llm.invoke(workflow_prompt)
    response_content = response.content
    try:
        # Extract JSON from the response
        json_match = re.search(r"\{.*\}", response_content, re.DOTALL)
        if json_match:
            workflow_json = json_match.group(0)
            workflow = json.loads(workflow_json)
        else:
            raise ValueError("No JSON content found in LLM response.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse workflow JSON: {e}")

    return workflow

# Execute Workflow
def execute_workflow(workflow, description: str):
    """
    Execute the dynamically generated workflow and return results.

    Args:
        workflow (dict): The generated workflow.
        description (str): The market description.

    Returns:
        dict: Execution results and the workflow structure.
    """
    step_outputs = []  # To store step-by-step outputs
    context = {"description": description}  # Shared context for steps

    for step in workflow["steps"]:
        step_id = step["id"]
        step_label = step["label"]
        step_input = step["input"]
        step_output_desc = step["output"]

        # Prepare the prompt for the LLM
        step_prompt = f"""
Please perform the following analysis step for the market description:

Market Description: "{description}"

Step: "{step_label}"

Instructions:
- Analyze the market description based on the step.
- Provide the output strictly in JSON format as per the expected output.
- Do not include any additional text or explanations.

Expected Output Format:
{{
    "result": ...  # Replace '...' with your result, following the expected output description.
}}

Example Output:
{{
    "result": true  # or false, or any other appropriate data type/value.
}}
"""

        # Invoke LLM
        response = llm.invoke(step_prompt)
        response_content = response.content.strip()

        # Extract JSON from the response
        try:
            json_match = re.search(r"\{.*\}", response_content, re.DOTALL)
            if json_match:
                step_result_json = json_match.group(0)
                step_result = json.loads(step_result_json)
                # Validate the output using StepOutput model
                try:
                    validated_output = StepOutput(**step_result)
                except ValidationError as ve:
                    print(f"Validation error in step {step_id}: {ve}")
                    validated_output = {"result": step_result}
            else:
                print(f"No JSON content found in step {step_id} response.")
                validated_output = {"result": response_content}
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON in step {step_id}: {e}")
            validated_output = {"result": response_content}

        # Save the output for this step
        step_outputs.append(
            {
                "step_id": step_id,
                "label": step_label,
                "output": validated_output.dict() if isinstance(validated_output, BaseModel) else validated_output,
            }
        )

    # Return workflow and step outputs
    return {
        "workflow": workflow,
        "execution_results": step_outputs,
    }

# API Endpoint
@app.post("/generate_and_execute_workflow/")
async def generate_and_execute_workflow_endpoint(request: BetRequest):
    """
    API endpoint to generate and execute a workflow for the given market description.

    Args:
        request (BetRequest): The input request containing the market description.

    Returns:
        dict: The workflow and execution results.
    """
    try:
        # Generate workflow
        workflow = generate_workflow(request.description)

        # Execute workflow
        result = execute_workflow(workflow, request.description)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Example Usage
if __name__ == "__main__":
    # Test Market Description
    test_description = "Will Bitcoin's price rise above $40,000 by November 18, 2024?"
    workflow = generate_workflow(test_description)
    execution_result = execute_workflow(workflow, test_description)

    print("Generated Workflow:", json.dumps(workflow, indent=2))
    print("Execution Result:", json.dumps(execution_result, indent=2))
