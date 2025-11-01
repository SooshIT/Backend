# 🔔 Real-Time Notifications System

## Overview

Complete notification system for Soosh platform with real-time updates, supporting multiple notification types and delivery channels.

---

## ✅ What's Been Implemented

### 1. **Database Schema** (`create_notifications_table.sql`)

#### Tables Created:

**`notifications`** - Main notifications table
- Notification types: `like`, `comment`, `reply`, `mention`, `follow`, `opportunity`, `booking`, `message`, `achievement`, `system`
- Fields: user_id, actor_id, title, message, related entity IDs
- State management: is_read, is_archived, read_at
- Metadata: JSONB for flexible additional data
- Action URL: Deep links for navigation

**`notification_preferences`** - User preferences
- Per-type notification toggles
- Delivery channel settings (push, email)
- Quiet hours configuration

**`device_tokens`** - Push notification tokens
- Support for iOS, Android, Web
- Device management and tracking

#### Helper Functions:
- `mark_notification_read(notification_id)` - Mark single notification as read
- `mark_all_notifications_read(user_id)` - Mark all as read
- `get_unread_notification_count(user_id)` - Get unread count

---

### 2. **Frontend UI**

#### Notifications Screen (`frontend/app/notifications.tsx`)

**Features:**
- ✅ All/Unread tabs with badge count
- ✅ Different icon and color for each notification type
- ✅ Actor avatars for user-triggered notifications
- ✅ Unread indicator (blue dot + left border)
- ✅ Pull-to-refresh
- ✅ Mark all as read button
- ✅ Empty state for no notifications
- ✅ Tap notification to navigate to related content

**Notification Types Supported:**
- 💗 **Like** - Red heart icon
- 💬 **Comment/Reply** - Teal message icon
- @ **Mention** - Blue at-sign icon
- 👤 **Follow** - Purple user-plus icon
- 💼 **Opportunity** - Green briefcase icon
- 📅 **Booking** - Orange calendar icon
- ✉️ **Message** - Blue mail icon
- 🏆 **Achievement** - Gold award icon
- 🔔 **System** - Gray bell icon

#### Notification Bell (`frontend/app/(tabs)/explore.tsx`)

**Features:**
- ✅ Bell icon in Discover header
- ✅ Red badge showing unread count (supports 99+)
- ✅ Tappable to open notifications screen

---

## 🚀 Implementing Real-Time Updates

### Option 1: WebSockets (Recommended)

**Backend (FastAPI with WebSockets):**

```python
# backend/api/websockets.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json

class NotificationManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_notification(self, user_id: str, notification: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(notification)

manager = NotificationManager()

@app.websocket("/ws/notifications/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(user_id)

# When creating a notification:
async def create_notification(user_id: str, notification_data: dict):
    # Save to database
    notification = await save_notification(notification_data)

    # Send real-time update
    await manager.send_notification(user_id, {
        "type": "new_notification",
        "notification": notification
    })
```

**Frontend (React Native):**

```typescript
// frontend/contexts/NotificationContext.tsx
import { useEffect, useState } from 'react';

export const useNotifications = (userId: string) => {
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket(`wss://your-api.com/ws/notifications/${userId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'new_notification') {
        setNotifications(prev => [data.notification, ...prev]);
        setUnreadCount(prev => prev + 1);

        // Show local notification
        showLocalNotification(data.notification);
      }
    };

    return () => ws.close();
  }, [userId]);

  return { notifications, unreadCount };
};
```

---

### Option 2: Server-Sent Events (SSE)

**Backend:**

```python
from fastapi.responses import StreamingResponse
import asyncio

@app.get("/notifications/stream")
async def notification_stream(user_id: str):
    async def event_generator():
        while True:
            # Check for new notifications
            notifications = await get_new_notifications(user_id)
            if notifications:
                yield f"data: {json.dumps(notifications)}\n\n"
            await asyncio.sleep(2)  # Poll every 2 seconds

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

**Frontend:**

```typescript
useEffect(() => {
  const eventSource = new EventSource(`/api/notifications/stream?user_id=${userId}`);

  eventSource.onmessage = (event) => {
    const notifications = JSON.parse(event.data);
    setNotifications(prev => [...notifications, ...prev]);
    setUnreadCount(prev => prev + notifications.length);
  };

  return () => eventSource.close();
}, [userId]);
```

---

### Option 3: Polling (Simplest)

**Frontend:**

```typescript
useEffect(() => {
  const fetchNotifications = async () => {
    const response = await fetch(`/api/notifications?user_id=${userId}&unread=true`);
    const data = await response.json();

    setUnreadCount(data.unread_count);
    setNotifications(data.notifications);
  };

  // Poll every 30 seconds
  const interval = setInterval(fetchNotifications, 30000);
  fetchNotifications(); // Initial fetch

  return () => clearInterval(interval);
}, [userId]);
```

---

## 🔥 Backend API Endpoints to Create

### 1. **Get Notifications**
```
GET /api/v1/notifications
Query params: user_id, limit, offset, unread_only
Response: { notifications: [...], unread_count: 5 }
```

### 2. **Mark as Read**
```
POST /api/v1/notifications/{notification_id}/read
Response: { success: true }
```

### 3. **Mark All as Read**
```
POST /api/v1/notifications/read-all
Body: { user_id }
Response: { updated_count: 10 }
```

### 4. **Get Unread Count**
```
GET /api/v1/notifications/unread-count
Query params: user_id
Response: { count: 5 }
```

### 5. **Update Preferences**
```
PUT /api/v1/notifications/preferences
Body: { likes_enabled: true, comments_enabled: false, ... }
Response: { success: true }
```

---

## 📲 Push Notifications

### Setup with Expo Notifications

```typescript
// frontend/services/pushNotifications.ts
import * as Notifications from 'expo-notifications';

export async function registerForPushNotifications() {
  const { status } = await Notifications.requestPermissionsAsync();

  if (status === 'granted') {
    const token = await Notifications.getExpoPushTokenAsync();

    // Send token to backend
    await fetch('/api/v1/device-tokens', {
      method: 'POST',
      body: JSON.stringify({
        token: token.data,
        device_type: Platform.OS,
      }),
    });
  }
}

// Handle received notifications
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});
```

---

## 🧪 Testing

### Create Test Notifications

```sql
-- Insert test notification
INSERT INTO notifications (
    user_id,
    notification_type,
    title,
    message,
    actor_id,
    actor_name,
    is_read
) VALUES (
    'your-user-id',
    'like',
    'New like on your post',
    'Sarah Johnson liked your achievement post',
    'actor-user-id',
    'Sarah Johnson',
    false
);
```

### Test with Mock Data

The notifications screen already has mock data. Just navigate to `/notifications` to see it in action.

---

## 🎯 Next Steps

1. **Implement WebSocket server** on backend
2. **Create notification API endpoints**
3. **Add notification triggers** when users:
   - Like posts/opportunities
   - Comment on posts
   - Book mentorship sessions
   - Follow other users
4. **Set up push notifications** with Expo
5. **Add notification preferences screen**
6. **Implement notification actions** (accept/decline booking, etc.)
7. **Add notification grouping** (e.g., "5 people liked your post")

---

## 💡 Advanced Features to Add Later

- **Notification Grouping**: Combine similar notifications ("John and 5 others liked your post")
- **Action Buttons**: Quick actions within notifications (Accept/Decline)
- **Notification History**: Archive and search old notifications
- **Smart Batching**: Group notifications during quiet hours
- **Read Receipts**: Track when notifications were seen
- **Priority Levels**: Urgent vs normal notifications
- **Rich Media**: Images and videos in notifications
- **Notification Templates**: Customizable notification formats

---

## 📊 Database Queries

### Get user's notifications:
```sql
SELECT
    n.*,
    u.first_name || ' ' || u.last_name as actor_full_name,
    u.profile_picture_url as actor_avatar
FROM notifications n
LEFT JOIN users u ON n.actor_id = u.id
WHERE n.user_id = 'user-id'
    AND n.is_deleted = false
ORDER BY n.created_at DESC
LIMIT 50;
```

### Get unread count:
```sql
SELECT COUNT(*)
FROM notifications
WHERE user_id = 'user-id'
    AND is_read = false
    AND is_deleted = false;
```

---

## ✅ Summary

You now have a **complete notification system** with:

✅ Database schema with 3 tables
✅ Helper functions for common operations
✅ Beautiful notifications UI with 9 notification types
✅ Notification bell with unread badge
✅ Tab filtering (All/Unread)
✅ Pull-to-refresh
✅ Empty states
✅ Documentation for real-time implementation

**To make it fully functional**, you need to:
1. Create backend API endpoints
2. Implement WebSocket or polling for real-time updates
3. Add notification triggers when events occur
4. Set up push notifications

The foundation is ready! 🎉
