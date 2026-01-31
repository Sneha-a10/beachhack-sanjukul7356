# How Requestly Works in This Architecture

Requestly acts as a **MITM (Man-in-the-Middle) Interceptor** and **Rule Engine** that sits between your code (the Client) and the Internet.

In our Maintenance Agent workflow, we are using it to **fake** a backend server that doesn't actually exist yet.

## The Workflow Visualization

```mermaid
sequenceDiagram
    participant Script as process_alert_workflow.py
    participant System as Network Layer
    participant Requestly as Requestly App/Extension
    participant Internet as Real Internet (dummy.local)

    Note over Script: 1. Script sends POST Request
    Script->>System: POST http://dummy.local/retrieve
    
    Note over System, Requestly: 2. Traffic Interception
    System->>Requestly: Intercepts outgoing request
    
    Note over Requestly: 3. Rule Matching
    Requestly->>Requestly: Checks "Mock Rules"
    Requestly->>Requestly: Match Found! (URL contains /retrieve)
    
    Note over Requestly: 4. Dynamic Response Generation
    Requestly->>Requestly: Runs JavaScript Rule
    Requestly->>Requestly: Reads "decision" from Body
    Requestly->>Requestly: Selects correct JSON chunk
    
    Note over Requestly, Script: 5. Return Mocked Response
    Requestly-->>Script: Returns 200 OK + JSON
    
    Note over Internet: The Request NEVER reaches here!
    Internet--xSystem: (Traffic was blocked/redirected)
```

## Key Concepts

### 1. Interception
Requestly hooks into the network stack (via Browser Extension or Desktop App VPN/Proxy). When your Python script tries to connect to `http://dummy.local`, Requestly sees this attempt **before** it leaves your computer.

### 2. DNS/Host Resolution
Normally, `dummy.local` would result in a "Could not resolve host" error (like I saw in my environment).
*   **With Requestly**: It recognizes the domain or URL pattern and says "I know this!" and takes over.

### 3. Rules Engine
We configured a **"Modify Response"** rule.
*   **Trigger**: `URL` contains `/retrieve` AND `Method` is `POST`.
*   **Action**: "Don't send this to the real internet. Instead, run this JavaScript code and send the *result* back to the client immediately."

### 4. The "Agentic" Benefit
This allows us to build the **Maintenance Agent** (Client) completely independently of the **Knowledge Base API** (Server).
*   We defined the *contract* (JSON input/output).
*   We *mocked* the server with Requestly.
*   We built the client to talk to that contract.

When the real backend is ready, you simply **turn off the Requestly rule**, and the Python script will instantly start talking to the real server without a single line of code change.
