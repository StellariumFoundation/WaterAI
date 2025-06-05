<script>
  import { onMount, onDestroy } from 'svelte';

  let message = '';
  let messages = [
    { id: 1, text: 'Hello from Water AI!', sender: 'ai' },
    { id: 2, text: 'Hi there! How can I help you today?', sender: 'user' },
    // Mock messages will be replaced by actual server interaction
  ];
  let socket = null;

  const wsUrl = 'ws://localhost:8000/ws';

  onMount(() => {
    console.log('Attempting to connect to WebSocket:', wsUrl);
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      console.log('WebSocket connection established.');
      // Optionally send an initial message or auth token
      // messages = [...messages, { id: Date.now(), text: 'Connected to server!', sender: 'ai' }];
    };

    socket.onmessage = (event) => {
      console.log('Message from server:', event.data);
      try {
        const receivedMsg = JSON.parse(event.data);
        // Ensure the message has the expected structure
        if (receivedMsg && typeof receivedMsg.text === 'string' && typeof receivedMsg.sender === 'string') {
          messages = [...messages, {
            id: Date.now(), // Or use an ID from the server if available
            text: receivedMsg.text,
            sender: receivedMsg.sender
          }];
        } else {
          console.warn('Received message in unexpected format:', receivedMsg);
          // Optionally, add a generic error or raw message to UI for debugging
          // messages = [...messages, { id: Date.now(), text: `Received unformatted: ${event.data}`, sender: 'ai' }];
        }
      } catch (e) {
        console.error('Error parsing message from server:', e);
        // Handle non-JSON messages or parsing errors
        messages = [...messages, {
          id: Date.now(),
          text: `Received non-JSON message: ${event.data}`, // Display raw message if not JSON
          sender: 'ai'
        }];
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      messages = [...messages, { id: Date.now(), text: 'Error connecting to server. Please try again later.', sender: 'ai' }];
    };

    socket.onclose = () => {
      console.log('WebSocket connection closed.');
      // Optionally, try to reconnect or inform the user
      // messages = [...messages, { id: Date.now(), text: 'Disconnected from server.', sender: 'ai' }];
    };
  });

  onDestroy(() => {
    if (socket) {
      socket.close();
      console.log('WebSocket connection closed on component destroy.');
    }
  });

  function sendMessage() {
    if (message.trim() === '' || !socket || socket.readyState !== WebSocket.OPEN) {
      if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.warn('WebSocket is not connected.');
        // Add a message to UI indicating connection issue
        messages = [...messages, { id: Date.now(), text: 'Not connected to server. Cannot send message.', sender: 'ai' }];
      }
      return;
    }

    const userMessage = { id: Date.now(), text: message, sender: 'user' };
    messages = [...messages, userMessage];

    // Send to backend via WebSocket
    // The backend should ideally broadcast this message back or send an AI response
    socket.send(JSON.stringify({ text: message })); // Send as JSON string

    message = ''; // Clear input field
  }
</script>

<div class="app-container">
  <header>
    <h1>Water AI</h1>
  </header>

  <main class="chat-area">
    {#each messages as msg (msg.id)}
      <div class="message {msg.sender === 'ai' ? 'ai-message' : 'user-message'}">
        <p>{msg.text}</p>
      </div>
    {/each}
  </main>

  <footer>
    <input
      type="text"
      bind:value={message}
      placeholder="Type your message..."
      on:keypress={(e) => e.key === 'Enter' && sendMessage()}
    />
    <button on:click={sendMessage}>Send</button>
  </footer>
</div>

<style>
  .app-container {
    display: flex;
    flex-direction: column;
    height: 100vh; /* Full viewport height */
    max-height: 100vh; /* Ensure it doesn't exceed viewport */
    width: 100%; /* Full width */
    max-width: 800px; /* Max width for larger screens */
    margin: 0 auto; /* Center on larger screens */
    border: 1px solid var(--border-color);
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    background-color: var(--background-main);
    overflow: hidden; /* Prevent content from spilling */
  }

  header {
    background-color: var(--header-bg);
    color: var(--text-color-light);
    padding: 0.75rem 1rem;
    text-align: center;
    border-bottom: 1px solid var(--border-color);
    flex-shrink: 0; /* Prevent header from shrinking */
  }

  header h1 {
    margin: 0;
    font-size: 1.75rem;
    font-weight: 500;
  }

  .chat-area {
    flex-grow: 1;
    padding: 1rem;
    overflow-y: auto; /* Enables scrolling for messages */
    display: flex;
    flex-direction: column;
    gap: 0.75rem; /* Space between messages */
    background-color: var(--background-main);
  }

  .message {
    padding: 0.6rem 0.9rem;
    border-radius: 12px; /* Softer, more modern border radius */
    margin-bottom: 0.25rem; /* Reduced from 0.5rem, gap handles spacing */
    max-width: 75%; /* Slightly increased max-width */
    word-wrap: break-word;
    line-height: 1.4;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }

  .user-message {
    background-color: var(--user-message-bg);
    color: var(--text-color-light);
    align-self: flex-end;
    border-bottom-right-radius: 4px; /* "Tail" effect */
  }

  .ai-message {
    background-color: var(--secondary-blue-light);
    color: var(--text-color-dark);
    align-self: flex-start;
    border-bottom-left-radius: 4px; /* "Tail" effect */
  }

  /* Small text for sender if ever needed, or for timestamps */
  .message p {
    margin: 0;
  }

  .message .sender-label { /* If you add sender labels above messages */
    font-size: 0.75em;
    color: #777;
    margin-bottom: 0.25em;
  }

  footer {
    display: flex;
    padding: 0.75rem 1rem;
    border-top: 1px solid var(--border-color);
    background-color: #ffffff; /* Slightly different from main bg for separation */
    align-items: center; /* Align items vertically */
    flex-shrink: 0; /* Prevent footer from shrinking */
  }

  footer input {
    flex-grow: 1;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 20px; /* Pill shape */
    margin-right: 0.75rem;
    font-size: 1rem;
    color: var(--text-color-dark);
    background-color: var(--input-bg);
  }

  footer input:focus {
    outline: none;
    border-color: var(--primary-blue);
    box-shadow: 0 0 0 2px var(--secondary-blue-light);
  }

  footer button {
    padding: 0.75rem 1.25rem;
    background-color: var(--button-bg);
    color: var(--text-color-light);
    border: none;
    border-radius: 20px; /* Pill shape */
    cursor: pointer;
    font-size: 1rem;
    font-weight: 500;
    transition: background-color 0.2s ease;
  }

  footer button:hover {
    background-color: var(--button-hover-bg);
  }

  footer button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
</style>
