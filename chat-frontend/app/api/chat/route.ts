import { NextRequest } from 'next/server'

/**
 * Process SSE response data by splitting into lines and extracting JSON
 */
function processSSEResponse(rawResponse: string): { jsonLines: string[], fullJson: string } {
  const jsonLines = rawResponse
    .split('\n')
    .filter(line => line.trim().startsWith('data:'))
    .map(line => line.replace(/^data:\s*/, ''))
  
  return {
    jsonLines,
    fullJson: jsonLines.join('')
  }
}

/**
 * Extract text content from response parts, handling both text and function responses
 */
function extractTextFromPart(part: any): string {
  if (part.text) {
    return part.text
  } else if (part.functionResponse) {
    return `Function called: ${part.functionResponse.name || 'unknown'}`
  }
  return ''
}

/**
 * Parse and process the API response data
 */
function parseAPIResponse(jsonLines: string[], fullJson: string): any {
  // If we have multiple JSON objects, try parsing each line individually
  if (jsonLines.length > 1) {
    const parsedLines = jsonLines
      .map((line, index) => {
        try {
          return JSON.parse(line)
        } catch (lineError) {
          console.error(`Error parsing JSON line ${index}:`, lineError)
          return null
        }
      })
      .filter(Boolean)
    
    if (parsedLines.length > 0) {
      return parsedLines
    }
  }
  
  // Single JSON object or fallback for multiple lines
  return JSON.parse(fullJson)
}

/**
 * Extract response text from parsed data
 */
function extractResponseText(data: any): string {
  // Handle single object response
  if (data.content && data.content.parts) {
    return data.content.parts
      .map(extractTextFromPart)
      .filter(Boolean)
      .join(' ')
  }
  
  // Handle array response
  if (Array.isArray(data)) {
    return data
      .map(event => {
        if (event.content && event.content.parts) {
          return event.content.parts
            .map(extractTextFromPart)
            .filter(Boolean)
            .join(' ')
        }
        return ''
      })
      .filter(Boolean)
      .join('\n')
  }
  
  // Fallback
  return JSON.stringify(data)
}

/**
 * Create a streaming response with the given text
 */
function createStreamResponse(text: string): Response {
  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode(`0:"${text.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"
`))
      controller.close()
    },
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  })
}

export async function POST(req: NextRequest) {
  try {
    const { messages } = await req.json()
    
    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      return new Response(JSON.stringify({ error: 'Invalid messages format' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    const lastMessage = messages[messages.length - 1]
    const adkApiUrl = process.env.ADK_API_URL || 'http://agent:8002'
    let responseText = ''
    
    try {
      // Prepare request to ADK API
      const requestBody = {
        appName: 'representation',
        userId: 'demo',
        sessionId: 'default_session',
        newMessage: {
          parts: [{ text: lastMessage.content }],
          role: 'user'
        },
        // streaming: true
        streaming: false
      }
      
      // Send request to ADK API
      const response = await fetch(`${adkApiUrl}/run_sse`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      })
      
      if (response.ok) {
        // Get and process the raw response
        const rawResponse = await response.text()
        
        // Process SSE format response
        const { jsonLines, fullJson } = processSSEResponse(rawResponse)
        
        try {
          // Parse the API response
          const data = parseAPIResponse(jsonLines, fullJson)
          
          // Extract text from the parsed data
          responseText = extractResponseText(data)
        } catch (parseError) {
          console.error('JSON parse error:', parseError)
          
          // Enhanced error logging for debugging
          if (parseError instanceof SyntaxError && parseError.message.includes('position')) {
            const position = parseInt(parseError.message.match(/position (\d+)/)?.[1] || '0')
            console.error(`Error context around position ${position}:`, 
              fullJson.substring(Math.max(0, position - 20), Math.min(fullJson.length, position + 20)))
          }
          throw parseError
        }
      }
    } catch (adkError) {
      console.error('ADK API error:', adkError)
    }
    
    // Fallback response if API call failed
    if (!responseText) {
      responseText = `收到您的消息："${lastMessage.content}"。ADK API服务异常，请稍后重试。`
    }

    return createStreamResponse(responseText)
  } catch (error) {
    console.error('Chat API error:', error)
    return new Response(JSON.stringify({ 
      error: error instanceof Error ? error.message : 'Internal server error' 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    })
  }
}
