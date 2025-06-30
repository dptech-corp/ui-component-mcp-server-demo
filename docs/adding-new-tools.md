# Adding New Tools to the Framework

## Overview
This guide explains how to add new tools to the ui-component-mcp-server-demo framework following the established patterns.

## Architecture Pattern
Each tool follows a consistent pattern:
1. **MCP Tools** - Define MCP server tools in `mcp-server/src/tools/`
2. **Backend Service** - Handle business logic and API endpoints
3. **Frontend Hook** - Manage state and API calls
4. **Frontend Component** - UI components integrated into Tools component
5. **SSE Events** - Real-time updates via Server-Sent Events

## Step-by-Step Guide

### 1. Create MCP Tools
Create a new file in `mcp-server/src/tools/your_tool_tools.py`:

```python
import uuid
import time
from fastmcp import FastMCP
from ..services.redis_client import RedisClient

def register_your_tool_tools(mcp: FastMCP, redis_client: RedisClient):
    @mcp.tool()
    async def your_tool_action(param: str) -> dict:
        """Execute your tool action with the given parameter."""
        message = {
            "id": str(uuid.uuid4()),
            "type": "your_tool_action",
            "timestamp": int(time.time() * 1000),
            "source": "mcp",
            "target": "your_tool_component",
            "component": "your_tool",
            "payload": {
                "action": "action_name",
                "data": {"param": param}
            }
        }
        await redis_client.publish_message("your_tool:actions", message)
        return {"success": True, "message": "Action completed"}

    @mcp.tool()
    async def list_your_tool_items() -> dict:
        """List all your tool items."""
        message = {
            "id": str(uuid.uuid4()),
            "type": "list_your_tool_items",
            "timestamp": int(time.time() * 1000),
            "source": "mcp",
            "target": "your_tool_component",
            "component": "your_tool",
            "payload": {
                "action": "list",
                "data": {}
            }
        }
        await redis_client.publish_message("your_tool:actions", message)
        return {"success": True, "message": "List request sent"}
```

### 2. Register MCP Tools
Add to `mcp-server/src/main.py`:

```python
from .tools.your_tool_tools import register_your_tool_tools

# In the main function, after other tool registrations:
register_your_tool_tools(mcp, redis_client)
```

### 3. Create Backend Service
Create `backend/app/services/your_tool_service.py`:

```python
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.your_tool import YourToolItem
from ..database import get_db

class YourToolService:
    def __init__(self, db: Session):
        self.db = db

    async def get_all_items(self) -> List[YourToolItem]:
        return self.db.query(YourToolItem).all()

    async def create_item(self, title: str, description: Optional[str] = None) -> YourToolItem:
        item = YourToolItem(title=title, description=description)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    async def update_item(self, item_id: str, **updates) -> Optional[YourToolItem]:
        item = self.db.query(YourToolItem).filter(YourToolItem.id == item_id).first()
        if item:
            for key, value in updates.items():
                setattr(item, key, value)
            self.db.commit()
            self.db.refresh(item)
        return item

    async def delete_item(self, item_id: str) -> bool:
        item = self.db.query(YourToolItem).filter(YourToolItem.id == item_id).first()
        if item:
            self.db.delete(item)
            self.db.commit()
            return True
        return False
```

Create API routes in `backend/app/routers/your_tool.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..services.your_tool_service import YourToolService
from ..schemas.your_tool import YourToolItemCreate, YourToolItemResponse

router = APIRouter(prefix="/api/your-tool", tags=["your-tool"])

@router.get("/", response_model=List[YourToolItemResponse])
async def get_items(db: Session = Depends(get_db)):
    service = YourToolService(db)
    return await service.get_all_items()

@router.post("/", response_model=YourToolItemResponse)
async def create_item(item: YourToolItemCreate, db: Session = Depends(get_db)):
    service = YourToolService(db)
    return await service.create_item(item.title, item.description)

@router.put("/{item_id}", response_model=YourToolItemResponse)
async def update_item(item_id: str, updates: dict, db: Session = Depends(get_db)):
    service = YourToolService(db)
    item = await service.update_item(item_id, **updates)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.delete("/{item_id}")
async def delete_item(item_id: str, db: Session = Depends(get_db)):
    service = YourToolService(db)
    success = await service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}
```

### 4. Create Frontend Hook
Create `frontend/src/hooks/useYourTool.ts` following the pattern of useTodos:

```typescript
// @ts-ignore - 忽略 React 模块类型声明错误
import { useState, useEffect } from 'react';
import { useSSE } from '@/contexts/SSEContext';
import type { YourToolItem } from '@/types/your-tool';

export function useYourTool() {
  const [items, setItems] = useState<YourToolItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { lastEvent } = useSSE();

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchItems = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiUrl}/api/your-tool`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setItems(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch items');
      console.error('Error fetching items:', err);
    } finally {
      setLoading(false);
    }
  };

  const addItem = async (title: string, description?: string) => {
    try {
      setLoading(true);
      const response = await fetch(`${apiUrl}/api/your-tool`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title, description }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      await fetchItems();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add item');
      console.error('Error adding item:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateItem = async (id: string, updates: Partial<YourToolItem>) => {
    try {
      setLoading(true);
      const response = await fetch(`${apiUrl}/api/your-tool/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      await fetchItems();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update item');
      console.error('Error updating item:', err);
    } finally {
      setLoading(false);
    }
  };

  const deleteItem = async (id: string) => {
    try {
      setLoading(true);
      const response = await fetch(`${apiUrl}/api/your-tool/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      await fetchItems();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete item');
      console.error('Error deleting item:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (lastEvent) {
      switch (lastEvent.event) {
        case 'your_tool_added':
        case 'your_tool_updated':
        case 'your_tool_deleted':
          fetchItems();
          break;
      }
    }
  }, [lastEvent]);

  useEffect(() => {
    fetchItems();
  }, []);

  return {
    items,
    loading,
    error,
    addItem,
    updateItem,
    deleteItem,
    refetch: fetchItems,
  };
}
```

### 5. Create Frontend Components
Create your tool components in `frontend/src/components/YourTool/`:

```typescript
// YourToolInput.tsx
interface YourToolInputProps {
  onAdd: (title: string, description?: string) => void;
  disabled?: boolean;
}

export function YourToolInput({ onAdd, disabled }: YourToolInputProps) {
  // Implementation similar to TodoInput
}

// YourToolItem.tsx
interface YourToolItemProps {
  item: YourToolItem;
  onUpdate: (id: string, updates: Partial<YourToolItem>) => void;
  onDelete: (id: string) => void;
  disabled?: boolean;
}

export function YourToolItemComponent({ item, onUpdate, onDelete, disabled }: YourToolItemProps) {
  // Implementation similar to TodoItemComponent
}
```

### 6. Integrate into Tools Component
Add your tool tab and content to `frontend/src/components/Tools/Tools.tsx`:

```typescript
// Add import
import { useYourTool } from '@/hooks/useYourTool';
import { YourToolInput } from './YourTool/YourToolInput';
import { YourToolItemComponent } from './YourTool/YourToolItem';

// Update interface
interface ToolsProps {
  activeTab: 'todo' | 'backlog' | 'terminal' | 'approval' | 'your-tool';
  setActiveTab: (tab: 'todo' | 'backlog' | 'terminal' | 'approval' | 'your-tool') => void;
  // ... other props
}

// Add hook usage
const {
  items: yourToolItems,
  loading: yourToolLoading,
  error: yourToolError,
  addItem: addYourToolItem,
  updateItem: updateYourToolItem,
  deleteItem: deleteYourToolItem,
} = useYourTool();

// Add SSE event handling
case 'your_tool_added':
case 'your_tool_updated':
case 'your_tool_deleted':
  // Events are handled by the hook
  break;

// Add tab button
<button
  onClick={() => setActiveTab('your-tool')}
  className={`px-4 py-2 text-sm font-medium rounded-t-lg ${
    activeTab === 'your-tool'
      ? 'bg-white border-b-2 border-blue-500 text-blue-600'
      : 'text-gray-500 hover:text-gray-700'
  }`}
>
  Your Tool
</button>

// Add tab content
) : activeTab === 'your-tool' ? (
  <>
    <YourToolInput onAdd={addYourToolItem} disabled={yourToolLoading} />
    <div className="space-y-2">
      {yourToolItems.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No items yet</p>
          <p className="text-sm mt-1">Add your first item!</p>
        </div>
      ) : (
        yourToolItems.map((item) => (
          <YourToolItemComponent
            key={item.id}
            item={item}
            onUpdate={updateYourToolItem}
            onDelete={deleteYourToolItem}
            disabled={yourToolLoading}
          />
        ))
      )}
    </div>
  </>
```

## Key Principles

### SSE Architecture
- **SSEContext** handles only basic connection logic
- **Tools component** processes SSE events and coordinates tool interactions
- **Individual hooks** manage their own state and API calls
- **SSE events** trigger hook refreshes rather than direct state updates

### Data Flow Pattern
1. User action triggers API call via hook
2. Backend processes request and publishes Redis message
3. SSE service receives Redis message and sends SSE event
4. Tools component receives SSE event and triggers hook refresh
5. Hook fetches updated data from API
6. UI updates with new data

### Naming Conventions
- MCP tools: `your_tool_action`, `list_your_tool_items`
- Backend routes: `/api/your-tool`
- Frontend hooks: `useYourTool`
- SSE events: `your_tool_added`, `your_tool_updated`, `your_tool_deleted`
- Components: `YourToolInput`, `YourToolItemComponent`

### Error Handling
- Always include try-catch blocks in API calls
- Set loading states during async operations
- Display error messages to users
- Log errors to console for debugging

### TypeScript Types
Create type definitions in `frontend/src/types/your-tool.ts`:

```typescript
export interface YourToolItem {
  id: string;
  title: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
}

export interface YourToolItemCreate {
  title: string;
  description?: string;
}
```

## Testing Your New Tool

1. **Start the development environment:**
   ```bash
   docker-compose up -d mysql redis
   cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
   cd frontend && npm run dev &
   ```

2. **Test the workflow:**
   - Create new items via UI
   - Verify real-time updates via SSE
   - Test MCP tool integration
   - Confirm error handling

3. **Verify SSE connection:**
   - Open browser DevTools → Network tab
   - Confirm only one EventSource connection to `/events`
   - Check that your tool events are received

## Common Pitfalls

1. **Multiple SSE connections:** Always use the shared SSEContext, never create additional EventSource instances
2. **Direct state updates:** Let hooks manage their own state, don't update from SSE events directly
3. **Missing error handling:** Always include proper error handling in API calls
4. **Inconsistent naming:** Follow the established naming conventions
5. **Forgetting MCP registration:** Remember to register your MCP tools in main.py

## Framework Benefits

This architecture provides:
- **Scalability:** Easy to add new tools following the same pattern
- **Consistency:** All tools work the same way
- **Real-time updates:** SSE events keep UI synchronized
- **Separation of concerns:** Clear boundaries between components
- **Type safety:** Full TypeScript support
- **Error resilience:** Proper error handling throughout

Follow this guide to maintain consistency and ensure your new tools integrate seamlessly with the existing framework.
