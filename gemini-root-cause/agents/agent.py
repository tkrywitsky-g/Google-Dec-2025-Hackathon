
import pandas as pd
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import FunctionTool
from google.adk.models import Gemini

model = Gemini(model_name="gemini-2.5-pro")


def read_logs(file_paths: list[str]) -> str:
    """
    Reads the content of specified CSV files and returns them as a single string.

    Args:
        file_paths: A list of paths to the CSV files.

    Returns:
        A string containing the concatenated content of the CSV files.
    """
    all_logs = ""
    for path in file_paths:
        try:
            df = pd.read_csv(path)
            all_logs += f"--- {path} ---\n"
            all_logs += df.to_string()
            all_logs += "\n\n"
        except FileNotFoundError:
            all_logs += f"--- {path} ---\n"
            all_logs += "File not found.\n\n"
    return all_logs

def get_weather_report(date: str, location: str) -> str:
    """
    Reads weather data from a CSV and returns the report for a given date and location.
    """
    try:
        weather_df = pd.read_csv("data/weather.csv")
        # Convert timestamp to datetime objects
        weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])
        # Filter by date
        report_df = weather_df[weather_df['timestamp'].dt.date == pd.to_datetime(date).date()]
        # Filter by location (case-insensitive)
        report_df = report_df[report_df['location'].str.contains(location, case=False)]
        if not report_df.empty:
            return report_df.to_string()
        else:
            return "No weather data found for the specified date and location."
    except FileNotFoundError:
        return "Weather data file not found."

def send_email(to: str, subject: str, body: str) -> str:
    """
    Sends an email.
    """
    # In a real scenario, this would use an email API.
    # For this example, it returns a confirmation message.
    return f"Email sent to {to} with subject '{subject}'."

def update_servicenow_case(case_number: str, comment: str) -> str:
    """
    Updates a ServiceNow case with a comment.
    """
    # In a real scenario, this would use the ServiceNow API.
    # For this example, it returns a confirmation message.
    return f"ServiceNow case {case_number} updated with comment: '{comment}'."

def create_rca_agent():
    """Creates the Root Cause Analysis agent pipeline."""
    researcher = Agent(
        model=model,
        name="NetworkLogResearcher",
        description="Analyzes network logs to find critical incidents.",
        instruction="""
        You are a network log researcher. Your job is to analyze the provided logs.
        1. Read the ServiceNow and Versa SD-WAN logs using the read_logs tool.
        2. Identify the critical incident from the ServiceNow tickets.
        3. Correlate the incident timestamp with events in the Versa SD-WAN logs.
        4. Summarize the key events that occurred around the time of the incident.
        Focus on events like VRRP flapping, packet loss, and tunnel drops.
        """,
        tools=[FunctionTool(read_logs)],
    )

    hypothesizer = Agent(
        model=model,
        name="NetworkAnalyst",
        description="Forms a hypothesis based on the researcher's findings.",
        instruction="""
        You are a network analyst. Your job is to form a hypothesis based on the researcher's findings.
        1. Review the summary of correlated log events.
        2. Use the get_weather_report tool for the date of the incident (July 24, 2025) and the affected location (Calgary).
        3. Based on the logs and the weather report, determine the most likely root cause.
        The hypothesis should connect the weather to the network instability. For example, a storm could cause power issues, leading to the observed VRRP flapping.
        """,
        tools=[FunctionTool(get_weather_report)],
    )

    dispatcher = Agent(
        model=model,
        name="DispatchCoordinator",
        description="Recommends an action based on the hypothesis.",
        instruction="""
        You are a dispatch coordinator. Your job is to recommend an action based on the hypothesis.
        1. Review the hypothesis provided by the analyst.
        2. Recommend a clear, actionable step for the field operations team. This can include commands to run.
        3. Propose sending an email to notify the network operations team.
        4. Propose updating the ServiceNow case to add the findings.
        5. The final recommendation should be a summary of the proposed actions.
        Example actions: 'Dispatch field tech for power checks at affected sites. Propose sending email to ops team and updating ServiceNow case.'
        """,
    )

    rca_agent = SequentialAgent(
        name="rca_agent",
        sub_agents=[researcher, hypothesizer, dispatcher]
    )
    return rca_agent

