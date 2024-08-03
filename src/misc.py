import os
from src.llms.assistant import app

# Assuming 'app' is already defined and 'app.get_graph()' returns the graph object
output_path = os.path.join(os.getcwd(), "graph.png")

try:
    png_data = app.get_graph().draw_mermaid_png()
    with open(output_path, "wb") as f:
        f.write(png_data)
    print(f"Graph saved as PNG at {output_path}")
except Exception as e:
    # Handle the exception or log it
    print(f"An error occurred: {e}")
