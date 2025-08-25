oila yFiles Graph Visualization
Overview
This project attempts to create an interactive graph visualization using yFiles and Voila. The goal is to display an ontology graph with interactive features.
Current Implementation
Core Components
graph_display.py: Main class for graph visualization using yFiles
display_notebook.ipynb: Jupyter notebook that creates and displays the graph
graphbuilder: yFiles graph builder module for creating and styling graphs
Basic Graph Display
Currently working with basic graph display showing nodes and edges. No interactive features yet.
Attempted Features & Issues
1. Interactive Widgets
Attempted: Adding buttons and controls using ipywidgets
Status: Failed
Error: Voila kernel connection issues and widget display problems
Last Try: Used debug flags but still encountered kernel issues
2. Dashboard Layout
Attempted: Creating a complete dashboard with title, controls, and graph
Status: Failed
Issue: Integration problems between HTML elements and ipywidgets
3. Basic Graph Display
Status: Working
Features:
Rectangle nodes for classes
Directed edges for properties
Basic styling (colors, fonts, shapes)
Running the Visualization
pip install voila
pip install ipywidgets
Ensure dependencies are installed:
2. Run with Voila:
voila display_notebook.ipynb
Next Steps & Alternatives to Consider
Alternative Approaches:
Consider using Streamlit instead of Voila
Explore FastAPI/Flask for serving the visualization
Look into other graph visualization libraries
Potential Improvements:
Implement proper widget integration
Add interactive graph controls
Improve error handling and debugging
Add proper documentation
Current Limitations
Widget integration not working
Limited interactive features
Debug information not easily accessible
Kernel connection issues with Voila
Dependencies
Python 3.12.6
Voila
ipywidgets
yFiles for Jupyter