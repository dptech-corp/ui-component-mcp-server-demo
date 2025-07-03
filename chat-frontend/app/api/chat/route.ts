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
    
    const adkApiUrl = process.env.ADK_API_URL || 'http://agent:8002'
    
    let responseText = ''
    
    try {
      const response = await fetch(`${adkApiUrl}/run_sse`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          appName: 'chat',
          userId: 'default-user',
          sessionId: 'default-session',
          newMessage: {
            parts: [
              {
                text: lastMessage.content
              }
            ],
            role: 'user'
          },
          streaming: false
        }),
      })

      if (response.ok) {
        const data = await response.json()
        
        if (Array.isArray(data)) {
          responseText = data
            .map((event: any) => {
              if (event.content && event.content.parts) {
                return event.content.parts
                  .map((part: any) => part.text || '')
                  .filter((text: string) => text.length > 0)
                  .join(' ')
              }
              return ''
            })
            .filter((text: string) => text.length > 0)
            .join('\n')
        } else {
          responseText = JSON.stringify(data)
        }
      }
    } catch (adkError) {
      console.error('ADK API error:', adkError)
    }
    
    if (!responseText) {
      responseText = `收到您的消息："${lastMessage.content}"。目前ADK API服务暂时不可用，这是一个模拟响应。请检查agent服务是否正常运行。\n\n作为科学代理，我可以帮助您：\n- 分析材料数据\n- 处理实验结果\n- 提供研究建议\n- 协助文献调研\n\n请在ADK服务恢复后重新尝试获得完整功能。`
    }

    const encoder = new TextEncoder()
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode(`0:"${responseText.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"\n`))
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
