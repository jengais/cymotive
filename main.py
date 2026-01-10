
import asyncio
import pandas as pd
from graph.builder import app



async def query(df):

    # Create a list of coroutines
    coros = []
    for _, row in df.iterrows():
        initial_state = {"report": row["report"]}
        coros.append(app.ainvoke(initial_state))

    # Execute all tasks in parallel and wait for all to finish
    # This is much faster for batch processing
    results = await asyncio.gather(*coros)

    # Print Output
    for i, res in enumerate(results):
        print(f"\n[INCIDENT {i+1}]: {df.iloc[i]['incident_id']}")
        print(f"Retrieved Context: {len(res.get('context', []))} similar cases found.")
        print(f"Report: {res['report']}")
        print(f"Summary: {res['summary']}")
        print(f"Mitigation: {res['mitigation']}")        
        print("-" * 50)

    print(f"\n✅ Processing Success ✅\n")




if __name__ == "__main__":
    df = pd.read_csv("samples/input_sample.csv")
    print(f"--- Starting Processing of {len(df)} Incidents ---\n\n")
    
    asyncio.run(query(df))
