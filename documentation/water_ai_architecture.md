# Water AI Architecture Overview

This document outlines the architecture of the Water AI system, a modular framework designed for building and running autonomous AI agents.

## High-Level Architecture

The system is composed of several key components that interact to enable an agent to understand instructions, use tools, and achieve goals.

```mermaid
graph TD
    A[User/System Instruction] --> B(Agent Core Logic);

    subgraph Agent Components
        B
        E[AgentToolManager]
    end

    subgraph LLM_Interaction_Layer [LLM Interaction Layer]
        C{LLM Client}
        H(MessageHistory)
        I(ContextManager)
    end

    subgraph Available_Capabilities [Available Capabilities]
        F[Tools (e.g., Web Search, File I/O)]
    end

    B --> H;
    B --> I;
    H --> C;
    I --> C;

    B --> C;
    C --> D[Large Language Model (LLM)];
    D --> C;
    C --> B;

    B --> E;
    E --> F;
    F --> E;
    E --> B;

    B --> G[Output/Action];

    style B fill:#cce5ff,stroke:#333,stroke-width:2px;
    style C fill:#e5ccff,stroke:#333,stroke-width:2px;
    style E fill:#fff2cc,stroke:#333,stroke-width:2px;
    style F fill:#ccffcc,stroke:#333,stroke-width:2px;
    style D fill:#ffcccc,stroke:#333,stroke-width:2px;
    style H fill:#e5ccff,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5;
    style I fill:#e5ccff,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5;
    style LLM_Interaction_Layer fill:#f0e6ff,stroke:#333,stroke-width:2px;
    style Agent_Components fill:#e6f2ff,stroke:#333,stroke-width:2px;
    style Available_Capabilities fill:#e6ffe6,stroke:#333,stroke-width:2px;
```

**Core Interaction Flow:**

1.  **Instruction Input**: The process begins with an initial instruction or prompt given to the **`Agent Core Logic`** (e.g., `AnthropicFC`).
2.  **LLM Communication**:
    *   The Agent, using an **`LLM Client`** (like `AnthropicLLMClient`), formats the instruction and conversation history (managed by **`MessageHistory`** and **`ContextManager`**) into a request for a **`Large Language Model (LLM)`**.
    *   The LLM processes the request and returns a response. This response might be a direct answer or a request to use one of the available tools.
3.  **Tool Use**:
    *   If the LLM requests a tool, the Agent utilizes the **`AgentToolManager`** to identify and execute the appropriate **`Tool`** (e.g., `web_search`, `read_file`).
    *   The **`AgentToolManager`** invokes the tool's implementation, and the result is captured.
    *   This result is then sent back to the LLM (via the **`LLMClient`**) as part of the ongoing conversation, allowing the LLM to use this new information.
4.  **Loop or Output**:
    *   The Agent continues this cycle of LLM interaction and tool use until the initial instruction is fulfilled or a stopping condition is met.
    *   The final result is then provided as an **Output/Action**.

The subsequent sections detail each of these components and their sub-directories.

# Agent (`agents` directory)

The `agents` directory contains the core logic for the AI agents.

## `BaseAgent`

`BaseAgent` is an abstract base class that defines the common interface for all agents. It outlines the basic functionalities and properties that an agent should possess, such as the ability to process instructions, interact with a language model, and handle responses. Concrete agent implementations inherit from this class.

## `AnthropicFC`

`AnthropicFC` is a concrete implementation of `BaseAgent`, specifically designed to work with Anthropic's language models that support function calling (or tool use).

### Main Agent Loop

The main operational loop in `AnthropicFC` can be summarized as follows:

1.  **Instruction Processing**: The agent receives initial instructions or a prompt. This typically defines the agent's goal or the task it needs to accomplish.
2.  **LLM Interaction**: The agent formats the instructions and any previous conversation history (managed with `MessageHistory` and `ContextManager`) into a request for the Anthropic LLM via the `LLMClient`.
3.  **Response Handling**: The LLM's response is processed.
    *   If the response contains a request to call a tool (function call), the agent proceeds to the tool calling step.
    *   If the response is a direct textual answer, this is typically considered the final output or a conversational reply.
4.  **Tool Calling**:
    *   The `AnthropicFC` agent utilizes an `AgentToolManager` instance to manage available tools.
    *   When the LLM requests a tool call, the agent identifies the requested tool and its parameters.
    *   The `AgentToolManager` is responsible for executing the tool with the provided parameters.
    *   The output or result from the tool execution is then captured.
5.  **Message Appending for Tool Use**: The result of the tool call is then formatted as a special message and appended to the `MessageHistory`. The agent then goes back to step 2 (LLM Interaction), sending the updated history back to the LLM. This allows the LLM to use the tool's output to inform its next step or final response.

This loop continues until the LLM provides a response that doesn't involve a tool call, or a predefined stop condition is met (e.g., maximum number of iterations).

## `AgentToolManager`

The `AgentToolManager` is a crucial component responsible for managing the tools available to an agent. Its responsibilities include:

*   Registering and storing available `LLMTool` instances.
*   Providing the schema of these tools to the LLM, so the LLM knows what functions it can request to be called and with what parameters.
*   Executing tool calls requested by the LLM, including parameter validation and dispatching the call to the appropriate tool implementation.
*   Returning the tool's output back to the agent.

By abstracting tool management, `AgentToolManager` allows for a clean separation of concerns, making it easier to add, remove, or modify tools without altering the core agent logic.

# LLM Interaction (`llm` directory)

The `llm` directory is responsible for abstracting the communication with various Large Language Models (LLMs). It provides a consistent interface for sending requests and receiving responses, regardless of the specific LLM provider being used.

## `LLMClient` Base Class

`LLMClient` is an abstract base class that defines the contract for all LLM-specific clients. It typically includes methods for:

*   Sending a prompt or a sequence of messages (prepared by the agent using `MessageHistory` and `ContextManager`) to the LLM.
*   Receiving the LLM's response, which might include text, tool calls, or other structured data.
*   Handling authentication and API-specific configurations.

The purpose of having specific clients like `AnthropicLLMClient`, `GeminiLLMClient`, and `OpenAILLMClient` (examples) is to encapsulate the unique API details, request/response formats, and authentication mechanisms of each LLM provider (Anthropic, Google Gemini, OpenAI respectively). This allows the core agent logic to remain provider-agnostic.

## `MessageHistory` Class

The `MessageHistory` class plays a vital role in managing the conversation flow with the LLM. Its primary responsibilities are:

*   **Storing Messages**: It keeps a chronological record of the conversation, including user prompts, LLM responses, tool call requests, and tool call results.
*   **Formatting for LLM**: It can format the stored messages into the specific structure required by the chosen `LLMClient`. Different LLMs expect conversation history in different formats.
*   **Context Window Management**: It works in conjunction with a `ContextManager` to manage the context window limitations of LLMs by truncating or summarizing older messages if the conversation becomes too long.
*   **Turn Management**: It helps differentiate between different turns in the conversation, which is crucial for understanding the sequence of interactions.

By centralizing message management, `MessageHistory` ensures that the agent can maintain context, provide relevant history to the LLM, and handle multi-turn conversations effectively.

## Data Structures for LLM Communication

To facilitate structured communication with LLMs, especially those supporting tool use/function calling, several data structures are employed:

*   **`ToolCall`**: This structure typically represents a request from the LLM to execute a specific tool. It includes:
    *   `tool_name`: The name of the tool to be called.
    *   `tool_id`: A unique identifier for this specific tool invocation, useful for matching results back to requests.
    *   `parameters`: A dictionary or object containing the arguments for the tool, as determined by the LLM.

*   **`TextPrompt`**: Represents a simple text message sent to the LLM, usually from the user or as a system instruction.

*   **`TextResult`**: Represents a simple text response from the LLM.

*   **`ToolResult`** (Conceptual): While not always a separate dedicated data structure returned by the tool itself, the agent system standardizes the representation of a tool's output when adding it to `MessageHistory`. This standardized representation typically includes:
    *   A `role` (e.g., "tool" or "function").
    *   The `tool_id` matching the original `ToolCall`.
    *   `content` representing the output of the tool (e.g., a string, JSON).

These data structures ensure that the information exchanged between the agent and the LLM is well-defined, making the interaction more robust and easier to debug.

# Context Management (`llm/context_manager` directory)

LLMs have a finite context window, meaning they can only process a limited amount of information at a time. The `llm/context_manager` directory provides strategies for managing the conversation history (stored in `MessageHistory`) to fit within these limits while retaining as much relevant information as possible. This is crucial for maintaining coherent and contextually aware conversations over extended interactions.

## `ContextManager` Base Class

The `ContextManager` is an abstract base class that defines the interface for all context management strategies. It typically dictates methods for:

*   Processing the current `MessageHistory`.
*   Pruning or transforming the history to fit within a specified token limit, according to its strategy.
*   Returning the modified list of messages ready to be sent to the LLM.

It works in conjunction with `MessageHistory` and a tokenizer associated with the target `LLMClient` to perform its duties.

## Context Management Strategies

Different strategies can be employed to manage context, each with its own trade-offs:

*   **`AmortizedForgettingContextManager`**: This strategy aims to gradually "forget" older information. It might, for example, remove the oldest messages once a certain threshold is passed, or remove messages based on their type (e.g., prioritize keeping system messages or summaries over individual user/assistant turns). The "amortized" aspect suggests that it tries to distribute the "cost" of forgetting over time rather than making drastic cuts.

*   **`LLMSummarizingContextManager`**: When the context window is nearing its limit, this strategy uses an LLM to summarize earlier parts of the conversation. The summary then replaces the detailed messages, freeing up tokens while attempting to preserve key information. This is more sophisticated but incurs the cost and latency of additional LLM calls for summarization.

*   **Simple Truncation**: The most basic strategy, where messages are removed from the beginning (or sometimes the end) of the conversation history once the token limit is exceeded. While simple, it can lead to abrupt loss of context.

The choice of strategy depends on the application's needs regarding memory, latency, and the importance of preserving long-range context.

## Token Counting and Truncation

A core function of any `ContextManager` is to accurately count the number of tokens that will be consumed by the messages when sent to the LLM.

*   **Token Counting**: This is usually done using a tokenizer specific to the LLM being used (e.g., Tiktoken for OpenAI models, or specific tokenizers for Anthropic/Gemini models). The `ContextManager` will tokenize the messages (often including not just the content but also identifiers for roles like "user", "assistant", "tool") to get an accurate count. Different LLMs have different tokenization methods and resulting token counts for the same text.

*   **Truncation/Modification**: If the total token count exceeds the LLM's maximum context window (or a configured lower limit), the `ContextManager` applies its strategy to reduce the number of tokens. This might involve:
    *   Removing whole messages (e.g., the oldest ones).
    *   Truncating the content within messages.
    *   Replacing messages with summaries.

The goal is to ensure that the messages sent to the LLM do not exceed its processing capacity, preventing API errors and ensuring efficient use of the model. System messages or initial prompts are often preserved to maintain the agent's core instructions.

# Tools (`tools` directory)

The `tools` directory contains the implementations of various capabilities that an agent can use to interact with its environment, gather information, or perform actions. These tools are crucial for extending the agent's abilities beyond simple text generation.

## `LLMTool` Base Class

`LLMTool` is an abstract base class that defines a standard interface for all tools that can be invoked by an LLM through an agent. Key attributes and methods include:

*   **`name` (string)**: A unique name for the tool. This is what the LLM uses to specify which tool it wants to call.
*   **`description` (string)**: A natural language description of what the tool does, its capabilities, and when an agent should consider using it. This description is provided to the LLM to help it decide when and how to use the tool.
*   **`input_schema` (JSON schema-like object, often a Pydantic model)**: Defines the structure, types, and constraints of the parameters the tool accepts. This allows the LLM to understand how to format its request for the tool and enables validation of the inputs.
*   **`run_impl(**kwargs)` (method)**: The actual implementation of the tool's logic. It takes keyword arguments corresponding to the `input_schema` and performs the tool's action. It returns a string or structured data representing the result of the tool's execution.

By adhering to this interface, tools can be seamlessly integrated into the agent's workflow.

## `AgentToolManager`

As previously mentioned in the "Agent (`agents` directory)" section, the `AgentToolManager` plays a central role in making tools available to the agent. Its responsibilities related to tools include:

*   **Registration**: It holds a collection of `LLMTool` instances that are available for the agent to use.
*   **Schema Generation**: It can generate a list of tool schemas (derived from each `LLMTool`'s `name`, `description`, and `input_schema`) to be provided to the LLM. This informs the LLM about the available tools and how to call them.
*   **Execution**: When the agent determines that an LLM is requesting a tool call (e.g., via a `ToolCall` object), the `AgentToolManager` looks up the appropriate tool by name and executes its `run_impl` method with the parameters provided by the LLM.
*   **Result Formatting**: It ensures the tool's output is returned to the agent in a consistent format, ready to be incorporated into the `MessageHistory`.

## `get_system_tools` Function

The `get_system_tools` function (or a similar mechanism) is typically used to dynamically assemble a list of `LLMTool` instances that should be made available to an agent at runtime. This allows for:

*   **Configurability**: Different agent instances or applications can be configured with different sets of tools based on their specific needs and permissions.
*   **Modularity**: Tools can be developed and maintained independently and then included or excluded as required.
*   **Context-Specificity**: In more advanced scenarios, the available tools might even change based on the current context of the conversation or task.

This function often reads a configuration file or takes arguments to determine which tool classes to instantiate and register with the `AgentToolManager`.

## Categories of Available Tools

The system provides a diverse range of tools, which can be broadly categorized as follows:

*   **Web Interaction**: Tools for fetching content from web pages, performing web searches, or interacting with web APIs.
*   **Browser Automation**: More advanced tools that can control a web browser to perform complex tasks like filling forms, clicking buttons, and navigating websites (e.g., using Selenium or Playwright). This allows agents to interact with sites that require JavaScript or have dynamic content.
*   **File System and Code Execution**: Tools for reading, writing, and modifying files, listing directory contents, and executing code (e.g., Python scripts). These require careful sandboxing and permissioning.
*   **Memory and Knowledge Management**: Tools that allow the agent to store information in a persistent or semi-persistent memory (e.g., a vector database or a simple key-value store) and retrieve it later. This helps agents maintain context over longer interactions or learn from past experiences.
*   **Advanced Tools**: This category can include more specialized tools like interacting with databases, version control systems (like Git), or specific productivity applications.

This structured approach to tools, combined with the `AgentToolManager`, provides a powerful and extensible way for agents to perform a wide variety of tasks.
