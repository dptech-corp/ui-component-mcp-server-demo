import { NextRequest } from 'next/server'

export async function GET(
  req: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const { sessionId } = params
    
    if (!sessionId) {
      return new Response(JSON.stringify({ error: 'Session ID is required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    const adkApiUrl = process.env.ADK_API_URL || 'http://localhost:8002'
    const historyUrl = `${adkApiUrl}/apps/representation/users/demo/sessions/${sessionId}`
    
    try {
      const response = await fetch(historyUrl, {
        method: 'GET',
        headers: {
          'accept': 'application/json'
        }
      })

      if (!response.ok) {
        console.warn(`Failed to load chat history from ${historyUrl}:`, response.status)
        return new Response(JSON.stringify({ 
          error: 'Failed to load chat history',
          status: response.status 
        }), {
          status: response.status,
          headers: { 'Content-Type': 'application/json' },
        })
      }

      const data = await response.json()
      
      return new Response(JSON.stringify(data), {
        status: 200,
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET',
          'Access-Control-Allow-Headers': 'Content-Type'
        },
      })
    } catch (fetchError) {
      console.error('Error fetching chat history:', fetchError)
      return new Response(JSON.stringify({ 
        error: 'Failed to fetch chat history',
        details: fetchError instanceof Error ? fetchError.message : 'Unknown error'
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      })
    }
  } catch (error) {
    console.error('Chat history API error:', error)
    return new Response(JSON.stringify({ 
      error: error instanceof Error ? error.message : 'Internal server error' 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    })
  }
}
