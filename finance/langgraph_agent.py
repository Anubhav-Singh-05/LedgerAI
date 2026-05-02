from langgraph.graph import StateGraph

def analysis_node(state):
    return state


graph = StateGraph(dict)
graph.add_node("analyze", analysis_node)
graph.set_entry_point("analyze")
graph.set_finish_point("analyze")

graph = graph.compile()
