export async function createSession(appName, userId) {
  try {
    const response = await fetch(`/apps/${appName}/users/${userId}/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ appName, userId }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('API Error Response (createSession):', response.status, errorText);
      throw new Error(`API Error: ${response.status} - ${errorText || 'Unknown error'}`);
    }

    const data = await response.json();
    return data.id; // Assuming the API returns { id: "..." }
  } catch (error) {
    console.error('Error creating session:', error);
    throw error;
  }
}

export async function* sendMessageToApi(message, appName, userId, sessionId) {
  try {
    const response = await fetch('/run_sse', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        appName: "agent",
        userId: userId,
        sessionId: sessionId,
        new_message: { parts: [{ text: message }], role: "user" },
      }),
    });

    if (!response.ok) {
      // Try to read as text if not OK, in case it's an error message
      const errorText = await response.text();
      console.error('API Error Response (not OK):', response.status, errorText);
      throw new Error(`API Error: ${response.status} - ${errorText || 'Unknown error'}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let result = '';
    

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      result += chunk;
      // console.log('Received chunk:', chunk); // Log each chunk

      // Process each complete SSE event
      const events = result.split('\n\n');
      result = events.pop(); // Keep incomplete event for next chunk

      for (const event of events) {
        if (event.startsWith('data:')) {
          try {
            const data = JSON.parse(event.substring(5));
            // console.log('Parsed SSE data:', data); // Log parsed data

            // Yield agent author for status updates
            if (data.author) {
              let statusMessage = `Agent: ${data.author} is thinking...`;
              if (data.functionCalls && data.functionCalls.length > 0) {
                const toolName = data.functionCalls[0].name;
                statusMessage = `Agent: ${data.author} is calling tool: ${toolName}...`;
              } else if (data.functionResponses && data.functionResponses.length > 0) {
                const toolName = data.functionResponses[0].name;
                statusMessage = `Agent: ${data.author} received response from: ${toolName}...`;
              }
              yield { type: 'status', message: statusMessage };
            }

            if (data.content) {
              // console.log('data.content:', data.content); // Log data.content
              if (data.content.parts && data.content.parts.length > 0) {
                const textPart = data.content.parts[0].text;
                // console.log('textPart:', textPart); // Log textPart
                if (textPart) {
                  yield { type: 'text', content: textPart };
                }
              }
            }
          } catch (e) {
            console.error('Error parsing SSE event:', e, 'Event string:', event);
          }
        }
      }
    }
    // No final return value needed for a generator
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}
