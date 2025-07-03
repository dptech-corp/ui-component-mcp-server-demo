import { NextRequest } from 'next/server'

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
    
    const response = await fetch('http://localhost:8002/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: lastMessage.content,
        session_id: 'default'
      }),
    })

    if (!response.ok) {
      throw new Error(`ADK API error: ${response.status}`)
    }

    const data = await response.json()
    
    const encoder = new TextEncoder()
    const stream = new ReadableStream({
      start(controller) {
        const responseText = Array.isArray(data.response) 
          ? data.response.map(event => event.content || JSON.stringify(event)).join('\n')
          : JSON.stringify(data.response)
        
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({
          type: 'text',
          content: responseText
        })}\n\n`))
        
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
