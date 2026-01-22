from langgraph.graph import StateGraph, END
from state import AgentState
from agents import reviewer_agent, developer_agent
from github_utils import get_pr_diff, post_pr_comment

# 1. Initialize the Graph with State definition
workflow = StateGraph(AgentState)

# 2. Add Nodes (Agents)
workflow.add_node("reviewer", reviewer_agent)
workflow.add_node("developer", developer_agent)

# 3. Define the Flow logic
workflow.set_entry_point("reviewer")

# 4. Define the "Conditional Edge" logic
def decide_to_continue(state: AgentState):
    """
    Determines if the graph should loop back for a fix or exit.
    """
    if state["is_approved"]:
        return "end"
    if state["revision_count"] >= 3: # Safety break to prevent infinite loops
        print("\n--- MAX REVISIONS REACHED: Terminating Workflow ---")
        return "end"
    return "continue"

# 5. Add the routing rules
workflow.add_conditional_edges(
    "reviewer",
    decide_to_continue,
    {
        "continue": "developer",
        "end": END
    }
)

# After the developer fixes the code, it always goes back to the reviewer
workflow.add_edge("developer", "reviewer")

# 6. Compile the graph into an executable application
app = workflow.compile()

# Execution Block
if __name__ == "__main__":
    # CONFIGURATION: Update these two values for your test
    # Format: "username/repository-name"
    REPO_NAME = "Ayushmaan101/PRdiff_test" 
    PR_NUMBER = 1 

    print(f"--- 1. FETCHING PR #{PR_NUMBER} FROM {REPO_NAME} ---")
    try:
        diff, title = get_pr_diff(REPO_NAME, PR_NUMBER)
        print(f"Successfully fetched PR: {title}\n")
    except Exception as e:
        print(f"Error fetching PR: {e}")
        exit()

    # Initial state for the graph
    inputs = {
        "code_snippet": diff,
        "review_comments": [],
        "is_approved": False,
        "revision_count": 0,
        "messages": []
    }

    print("--- 2. STARTING MULTI-AGENT REVIEW WORKFLOW ---")
    final_state = None
    
    # Run the graph and stream the updates from each node
    for output in app.stream(inputs):
        for key, value in output.items():
            # Update the local final_state variable with the latest data
            final_state = value 
            print(f"\n[NODE COMPLETED]: {key.upper()}")
            
            # Print a snippet of what happened for visibility
            if key == "reviewer":
                status = "APPROVED ✅" if value['is_approved'] else "CHANGES REQUESTED ❌"
                print(f"Status: {status}")
            elif key == "developer":
                print(f"Developer Revision Count: {value['revision_count']}")

    print("\n--- 3. WORKFLOW COMPLETE ---")

    # 7. Post the final result back to the GitHub PR
    if final_state:
        if final_state["is_approved"]:
            summary = "### ✅ AI Review: APPROVED\n"
            summary += f"The agent team has reviewed the PR and verified the fixes.\n\n"
            summary += f"**Final Revision:**\n{final_state['messages'][-1].content}"
        else:
            summary = "### ⚠️ AI Review: MAX REVISIONS REACHED\n"
            summary += "The agents were unable to reach an approved state within the revision limit. Please review the manual logs."
        
        try:
            post_pr_comment(REPO_NAME, PR_NUMBER, summary)
            print("Successfully posted the final review to GitHub.")
        except Exception as e:
            print(f"Error posting to GitHub: {e}")

    # OPTIONAL: Save the graph visualization
    try:
        app.get_graph().draw_mermaid_png(output_file_path="graph_viz.png")
        print("\nWorkflow visualization saved as 'graph_viz.png'")
    except:
        pass