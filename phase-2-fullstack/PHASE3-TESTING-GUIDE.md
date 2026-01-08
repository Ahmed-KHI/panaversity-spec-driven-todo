# Phase III Testing Guide

**Status:** Ready for Testing  
**Date:** January 8, 2026  
**Implementation:** Complete (T-001 to T-014)

---

## Prerequisites

✅ **Completed:**
- Database migration successful (conversations, messages tables created)
- Backend dependencies installed (openai>=1.54.0)
- PostCSS configuration fixed for Tailwind 4.0
- OPENAI_API_KEY added to backend/.env

---

## Local Testing Steps

### Step 1: Verify Servers Running

**Backend:** Should be running at http://localhost:8000
- Check: Open http://localhost:8000/docs
- Verify: Chat endpoint visible: `POST /api/{user_id}/chat`

**Frontend:** Should be running at http://localhost:3000
- Open: http://localhost:3000
- Verify: Login page loads

---

### Step 2: Authentication Test

1. **Login** with existing user or **Register** new account
2. Verify redirect to **/dashboard**
3. Verify **"💬 Chat with AI Assistant"** button appears

---

### Step 3: Chat Interface Test

1. Click **"Chat with AI Assistant"** button
2. Verify redirect to **/chat**
3. Verify chat interface renders:
   - Welcome message from AI
   - Input field at bottom
   - Send button

---

### Step 4: AI Agent Functionality Tests

#### Test 1: Create Task
**Input:** "Add task to buy groceries"

**Expected Response:**
```
✅ Added 'buy groceries' to your task list.
```

**Verification:**
- Go to Dashboard → Task appears in list
- Check database: `SELECT * FROM tasks WHERE title ILIKE '%groceries%';`

---

#### Test 2: List Tasks
**Input:** "Show me my tasks"

**Expected Response:**
```
Here are your X task(s):

1. buy groceries ⏳
```

**Verification:**
- All user's tasks displayed
- Completed tasks show ✅
- Pending tasks show ⏳

---

#### Test 3: Complete Task
**Input:** "Mark task 1 as complete"

**Expected Response:**
```
✅ Marked 'buy groceries' as complete!
```

**Verification:**
- Go to Dashboard → Task shows as completed
- Check database: `SELECT * FROM tasks WHERE id = 1;` → `completed = true`

---

#### Test 4: Update Task
**Input:** "Change task 1 to 'buy organic groceries'"

**Expected Response:**
```
✅ Updated 'buy organic groceries'
```

**Verification:**
- Task title updated in database
- Dashboard reflects new title

---

#### Test 5: Delete Task
**Input:** "Delete task 1"

**Expected Response:**
```
✅ Deleted 'buy organic groceries'
```

**Verification:**
- Task removed from Dashboard
- Database: Task no longer exists

---

### Step 5: Conversation Persistence Test

1. Send message: "Add task to call mom"
2. Refresh page (F5)
3. Verify: Conversation history loads
4. Send another message: "What tasks do I have?"
5. Verify: AI remembers previous context

**Database Check:**
```sql
-- Check conversation created
SELECT * FROM conversations WHERE user_id = '<your-user-id>';

-- Check messages stored
SELECT * FROM messages WHERE conversation_id = <id> ORDER BY created_at;
```

---

### Step 6: User Isolation Test

1. Login as **User A**
2. Create task via chat: "Add task to test isolation"
3. Note task ID
4. Logout
5. Login as **User B**
6. Try to access User A's task via chat
7. Verify: User B cannot see or modify User A's tasks

---

### Step 7: Error Handling Tests

#### Test: Empty Message
**Action:** Try to send empty message  
**Expected:** Button disabled, no request sent

#### Test: Long Message
**Action:** Send message > 2000 characters  
**Expected:** 422 error with message "Message must be under 2000 characters"

#### Test: Invalid Token
**Action:** Logout, try to access /chat directly  
**Expected:** Redirect to /login

---

## API Testing (Optional - Use Postman/Thunder Client)

### Endpoint: POST /api/{user_id}/chat

**Request:**
```json
{
  "conversation_id": null,
  "message": "Add task to test API"
}
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
Content-Type: application/json
```

**Expected Response:**
```json
{
  "conversation_id": 1,
  "response": "✅ Added 'test API' to your task list.",
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {
        "title": "test API"
      },
      "result": {
        "task_id": 42,
        "status": "created",
        "title": "test API"
      }
    }
  ]
}
```

---

## Database Verification

### Check Tables Created
```sql
\dt

-- Expected output:
-- conversations
-- messages
-- tasks
-- users
```

### Verify Indexes
```sql
\d conversations
\d messages

-- Expected indexes:
-- idx_conversations_user_id
-- idx_messages_conversation_id
-- idx_messages_user_id
-- idx_messages_created_at
```

### Sample Queries
```sql
-- Count conversations
SELECT COUNT(*) FROM conversations;

-- Count messages per conversation
SELECT conversation_id, COUNT(*) as message_count 
FROM messages 
GROUP BY conversation_id;

-- View recent conversations with message count
SELECT 
    c.id,
    c.user_id,
    c.created_at,
    COUNT(m.id) as message_count
FROM conversations c
LEFT JOIN messages m ON m.conversation_id = c.id
GROUP BY c.id
ORDER BY c.updated_at DESC
LIMIT 10;
```

---

## Performance Testing

### Response Time Targets
- ✅ Chat request processing: < 3s (includes OpenAI API call)
- ✅ Database queries: < 50ms
- ✅ Page load (chat page): < 2s

### Test Performance
1. Open browser DevTools → Network tab
2. Send chat message
3. Check request timing
4. Verify within targets

---

## Known Issues & Troubleshooting

### Issue: "Failed to process message"
**Cause:** OpenAI API error  
**Check:** 
- OPENAI_API_KEY is valid
- API key has credits
- Backend logs: `uv run fastapi dev src/main.py`

### Issue: Chat button not appearing
**Cause:** Frontend not updated  
**Solution:** Hard refresh (Ctrl+Shift+R)

### Issue: "Conversation not found"
**Cause:** Invalid conversation_id  
**Solution:** Set `conversation_id: null` to start new conversation

### Issue: Tasks not showing in list
**Cause:** User isolation working correctly  
**Verify:** Logged in with correct user

---

## Success Criteria Checklist

Phase III is ready for deployment when:

- [x] Database migration completed
- [ ] All 5 MCP tools work (add, list, complete, update, delete)
- [ ] Conversation persists across page refreshes
- [ ] User isolation enforced (cannot access other users' data)
- [ ] Chat UI renders correctly
- [ ] AI responses are relevant and helpful
- [ ] No console errors in browser
- [ ] No errors in backend logs
- [ ] Response times within targets
- [ ] Error handling works gracefully

---

## Next Steps After Testing

1. **Update README** with Phase III information
2. **Commit changes** to Git
3. **Deploy backend** to Hugging Face Spaces
4. **Deploy frontend** to Vercel
5. **Record demo video** (90 seconds)
6. **Submit** for evaluation

---

**Testing Status:** ⏳ In Progress  
**Last Updated:** January 8, 2026
