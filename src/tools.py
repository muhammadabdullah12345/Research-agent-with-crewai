from crewai_tools import SerperDevTool
from dotenv import load_dotenv

load_dotenv()

search_tool = SerperDevTool(n_results=5)