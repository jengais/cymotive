
import asyncio
import pandas as pd
from io import StringIO
from langgraph.graph import StateGraph, START, END

# Import your state and nodes
from utils.state import AgentState
from graph.builder import app

if __name__ == "__main__":


    # 3. Load incidents from CSV
    df = pd.read_csv("samples/input_sample.csv")
    
    print(f"--- Starting Processing of {len(df)} Incidents ---")
    
    # 4. Execute Workflow Asynchronously
    tasks = []
    for _, row in df.iterrows():
        # Initialize state for each incident
        initial_state = {"report": row["report"]}
        
        # Use ainvoke for non-blocking execution
        tasks.append(app.invoke(initial_state))

    # Wait for all incidents to be processed

    # 5. Print "Pretty" Output
    for i, res in enumerate(tasks):
        print(f"\n[INCIDENT {i+1}]: {df.iloc[i]['incident_id']}")
        print(f"Retrieved Context: {len(res.get('context', []))} similar cases found.")
        print(f"Report: {res['report']}")
        print(f"Summary: {res['summary']}")
        print(f"Mitigation: {res['mitigation']}")

        # print(f"Mitigation Plan: {res.get('mitigation')}")
        print("-" * 50)