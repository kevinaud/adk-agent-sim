# **Product Requirements Document: ADK Agent Simulator (adk\_agent\_sim)**

## **1\. Overview**

Project Name: adk\_agent\_sim  
Type: Python Library / Developer Tool  
Core Stack: Python, Streamlit, Google ADK (Agent Development Kit)

### **1.1. Problem Statement**

Developing "Agentic" AI systems involves giving Large Language Models (LLMs) access to executable tools (Python functions, APIs, MCP servers). When an agent fails to solve a task, it is difficult to determine the root cause:

1. **Model Failure:** Is the LLM not smart enough?  
2. **Context Failure:** Did the agent lack necessary information?  
3. **Tool Failure:** Are the tool definitions, descriptions, or parameters unintuitive or insufficient?

Currently, developers debug this by blindly tweaking prompts and re-running the stochastic LLM, which is inefficient.

### **1.2. Product Vision**

The **ADK Agent Simulator** is a "Wizard of Oz" (Human-in-the-Loop) tool. It provides a graphical interface that allows a human developer to "roleplay" as the Agent.

The developer sees exactly what the agent sees (instructions, available tools) and attempts to solve a user query manually by executing tools via the UI.

* **If the human cannot solve the task:** The toolset or context is insufficient. The agent definition must be fixed.  
* **If the human CAN solve the task:** The sequence of steps is recorded as a "Golden Trace" to be used as a ground-truth example for evaluating the LLM.

## **2\. Technical Architecture**

The system is designed as a **library**, not a standalone application. It follows the **Wrapper Pattern**, where the user provides the environment and the library provides the UI.

### **2.1. The Wrapper Pattern**

1. **The Host (User Script):** The developer creates a Python script (e.g., debug.py) that imports their project's instantiated ADK Agent objects. This ensures all environment variables, API keys, and database connections are initialized correctly by the user's existing code.  
2. **The Simulator (Library):** The user passes these agent instances to the AgentSimulator class. The library uses **Streamlit** to render a web interface that controls these agents.

### **2.2. The ADK Integration Layer**

Instead of implementing custom reflection logic to parse Python code, adk\_agent\_sim relies directly on the internal abstractions provided by the Google ADK.

* **Discovery:** Uses agent.canonical\_tools() to retrieve initialized tool instances.  
* **Schema:** Uses tool.\_get\_declaration() to retrieve the exact Gemini Function Declaration (JSON Schema) sent to the model.  
* **Execution:** Uses tool.run\_async() to execute tools. This abstracts away the difference between local FunctionTool execution and remote McpTool network calls.

## **3\. Functional Requirements**

### **3.1. Initialization & Configuration**

* **FR-01 (Entry Point):** The library must expose a main class AgentSimulator(agents: dict\[str, Agent\]).  
* **FR-02 (Agent Selection):** If multiple agents are provided, the UI must allow the user to toggle between them via a sidebar or dropdown.  
* **FR-03 (Agent Introspection):** Upon loading an agent, the system must display:  
  * **Name & Description:** For identification.  
  * **System Instructions:** Extracted via agent.canonical\_instruction(). This should be displayed prominently so the human actor understands the persona they are simulating.

### **3.2. Tool Discovery & Rendering**

The system must dynamically generate UI forms for any tool attached to the agent.

* **FR-04 (Tool List Retrieval):** The system must asynchronously await agent.canonical\_tools() to get the list of BaseTool objects.  
* **FR-05 (Schema Extraction):** The system must call \_get\_declaration() on each tool to obtain the FunctionDeclaration.  
* **FR-06 (Dynamic Form Generation):** The system must map the tool's parameter schema to Streamlit widgets:  
  * STRING → st.text\_input  
  * INTEGER / NUMBER → st.number\_input  
  * BOOLEAN → st.checkbox  
  * ENUM → st.selectbox  
  * Complex/Nested Objects → st.text\_area (parsed as JSON).  
* **FR-07 (Validation):** The UI should enforce basic type constraints (e.g., required fields) before allowing execution.

### **3.3. Execution Engine**

* **FR-08 (Context Mocking):** The system must construct a valid ToolContext (and InvocationContext) object, as these are required arguments for ADK tool execution methods.  
* **FR-09 (Async Execution):** The system must provide a mechanism to run the asynchronous tool.run\_async() method within the synchronous Streamlit environment.  
* **FR-10 (Error Handling):** If a tool execution raises an exception, the UI must catch it and display it as a "Tool Error" output, mimicking how an LLM would receive an error frame.

### **3.4. Session Recording (The "Run")**

The core workflow involves a human performing a multi-step task.

* **FR-11 (User Message):** The interface must allow the user to define the initial User Query (the problem to be solved).  
* **FR-12 (History Log):** The interface must display a chronological log of events:  
  1. User Message.  
  2. Tool Call (Input arguments).  
  3. Tool Output (Return value).  
* **FR-13 (Final Response):** The interface must provide a specific action to "End Turn" or "Submit Final Response," allowing the human to type the final text answer to the mock user.

### **3.5. Output & Export**

* **FR-14 (Golden Trace Export):** The system must allow the user to download the completed session as a JSON file.  
* **FR-15 (Schema Compliance):** The exported JSON must be structured to be compatible with ADK evaluation tools.

## **4\. Data Structures**

### **4.1. The Golden Trace Schema**

The output file represents a "perfect" execution of an agentic workflow.

JSON

{  
  "metadata": {  
    "agent\_name": "CalculatorAgent",  
    "timestamp": "2025-10-27T10:00:00Z",  
    "user\_query": "Calculate 5 \* 5 \+ 10"  
  },  
  "trace": \[  
    {  
      "step\_index": 0,  
      "type": "tool\_call",  
      "tool\_name": "multiply",  
      "arguments": { "a": 5, "b": 5 },  
      "output": 25  
    },  
    {  
      "step\_index": 1,  
      "type": "tool\_call",  
      "tool\_name": "add",  
      "arguments": { "a": 25, "b": 10 },  
      "output": 35  
    },  
    {  
      "step\_index": 2,  
      "type": "final\_answer",  
      "content": "The result is 35."  
    }  
  \]  
}

## **5\. User Workflow Example**

1. **Setup:** The developer creates demo.py:  
   Python  
   from my\_project.agents import math\_agent  
   from adk\_agent\_sim import AgentSimulator

   if \_\_name\_\_ \== "\_\_main\_\_":  
       AgentSimulator(agents={"Math Bot": math\_agent}).run()

2. **Launch:** Developer runs streamlit run demo.py.  
3. **Roleplay:**  
   * Developer inputs query: *"What is 50 times 10?"*  
   * Developer selects the multiply tool from the UI sidebar.  
   * The UI shows inputs for a and b. Developer enters 50 and 10\.  
   * Developer clicks "Run Tool".  
   * The main chat window shows the tool output: 500\.  
   * Developer types final response: *"The answer is 500"* and clicks "Finish".  
4. **Export:** Developer clicks "Download Trace" to save math\_eval\_01.json.

## **6\. Implementation Roadmap**

### **Phase 1: Core Bridge (MVP)**

* Implement AgentSimulator class structure.  
* Implement \_run\_async helper for Streamlit.  
* Implement introspection logic using agent.canonical\_tools().  
* Render a raw text dump of available tool schemas to verify ADK integration.

### **Phase 2: Dynamic UI**

* Implement schema-to-widget mapping logic (SchemaRenderer).  
* Create the "Run Tool" handler that calls tool.run\_async().  
* Implement basic ToolContext mocking.

### **Phase 3: Session Management**

* Implement SessionState to track the history of the conversation.  
* Build the Chat UI components to display the history log.  
* Implement the "Final Response" and JSON export functionality.
