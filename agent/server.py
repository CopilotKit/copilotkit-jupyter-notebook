from fastapi import FastAPI
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from copilotkit import LangGraphAGUIAgent
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

app = FastAPI()

# Default node function - can be replaced from notebook
async def default_node(state: MessagesState):
    model = ChatOpenAI(model="gpt-4o-mini")
    system_message = SystemMessage(content="You are a helpful assistant.")
    response = await model.ainvoke([system_message, *state["messages"]])
    return {"messages": response}

# Mutable reference to the node function
chat_node = default_node

# Wrapper that delegates to the mutable chat_node
async def chat_node_wrapper(state: MessagesState):
    return await chat_node(state)

# Build the graph with checkpointer for AG-UI
memory = MemorySaver()
graph = StateGraph(MessagesState)
graph.add_node("chat", chat_node_wrapper)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)
compiled_graph = graph.compile(checkpointer=memory)

# Add the endpoint
add_langgraph_fastapi_endpoint(
    app=app,
    agent=LangGraphAGUIAgent(
        name="sample_agent",
        description="A sample agent.",
        graph=compiled_graph,
    ),
    path="/",
)


@app.get("/health")
async def health():
    return {"status": "ok"}


def set_chat_node(node_fn):
    """Replace the chat node function from a notebook."""
    global chat_node
    chat_node = node_fn
