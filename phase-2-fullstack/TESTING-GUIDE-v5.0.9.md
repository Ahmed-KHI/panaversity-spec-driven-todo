# Testing Guide for v5.0.9 Bug Fixes

**Production URL:** http://34.93.106.63  
**Version:** 5.0.9  
**Deployment Date:** December 25, 2025  
**Status:** ✅ Deployed to GKE

---

## 🎯 What Was Fixed

This release fixes two critical production issues:

1. **Manual Task Edit/Update Not Working** → Now works with error feedback
2. **Advanced Search UI Missing** → Complete search/filter interface added

---

## 🧪 Test Plan

### Prerequisites

1. Open browser: http://34.93.106.63
2. Log in or register a new account
3. Create at least 3-5 test tasks with different attributes:
   - Mix of priorities (low, medium, high, urgent)
   - Some with due dates, some without
   - Some recurring, some one-time
   - Various tags (work, personal, urgent, etc.)

---

## Test 1: Manual Task Edit (Critical Bug Fix)

### Objective
Verify that manually editing tasks now works correctly.

### Steps

1. **Edit Task Title**
   - Click "Edit" button on any task
   - Change the title text
   - Click "Save"
   - ✅ **Expected:** Task updates immediately with new title
   - ❌ **Previous Bug:** Nothing happened, no error shown

2. **Update Priority**
   - Click "Edit" on a task
   - Change priority dropdown (e.g., medium → high)
   - Save
   - ✅ **Expected:** Task shows new priority badge color
   - Check badge updates (low=gray, medium=blue, high=orange, urgent=red)

3. **Add/Change Due Date**
   - Edit a task without due date
   - Select a date and time
   - Save
   - ✅ **Expected:** Task displays due date
   - Verify format: "Due: Dec 26, 2025 14:30"

4. **Enable Recurring Task**
   - Edit a one-time task
   - Check "Recurring" checkbox
   - Select frequency (e.g., "Weekly")
   - Save
   - ✅ **Expected:** Task shows recurring badge (🔁)
   - Badge should display frequency: "🔁 Weekly"

5. **Update Description**
   - Edit a task
   - Change description text
   - Save
   - ✅ **Expected:** Description updates in task card

6. **Test Error Handling**
   - Edit a task
   - Clear the title field (make it empty)
   - Try to save
   - ✅ **Expected:** Browser validation prevents submit ("Please fill out this field")
   
   OR (if backend error):
   - ✅ **Expected:** Red error box appears with message
   - Error should be user-friendly
   - Close button (✕) should dismiss error

7. **Console Check**
   - Open browser DevTools (F12)
   - Go to Console tab
   - Edit and save a task
   - ✅ **Expected:** See logs like:
     ```
     Updating task: { userId: "...", title: "...", ... }
     Task updated successfully: { id: 123, title: "...", ... }
     ```
   - ❌ **No errors should appear** (401, 500, etc.)

### Success Criteria

- [ ] All task fields update correctly
- [ ] Changes reflect immediately (no page refresh needed)
- [ ] No console errors during edit
- [ ] Error messages display if update fails
- [ ] Loading state shows during save
- [ ] Edit form closes after successful save

---

## Test 2: Advanced Search UI (New Feature)

### Objective
Verify the new Advanced Search component works and filters tasks correctly.

### Steps

1. **Locate Advanced Search**
   - Go to dashboard
   - Look for "🔍 Advanced Search" section above task stats
   - Click to expand if collapsed
   - ✅ **Expected:** Search panel expands with multiple filter options

2. **Search by Text**
   - Type keyword in "Search tasks..." input (e.g., "meeting")
   - Click "🔍 Apply Filters"
   - ✅ **Expected:** Only tasks with "meeting" in title/description shown
   - Check results count updates

3. **Filter by Priority**
   - Clear previous search (click "Clear All")
   - Open Priority dropdown
   - Select "High" and "Urgent" (Ctrl/Cmd + click for multiple)
   - Apply Filters
   - ✅ **Expected:** Only high/urgent priority tasks shown
   - Verify active filters summary shows: "Priority: High, Urgent"

4. **Filter by Status**
   - Select "Status: Pending" from dropdown
   - Apply Filters
   - ✅ **Expected:** Only incomplete tasks shown
   - Change to "Completed"
   - ✅ **Expected:** Only completed tasks shown

5. **Date Range Filter**
   - Set "Due After" to today's date
   - Set "Due Before" to 7 days from now
   - Apply Filters
   - ✅ **Expected:** Only tasks due within next week shown
   - Tasks without due dates should be excluded

6. **Recurring Task Filter**
   - Select "Task Type: Recurring Only"
   - Apply Filters
   - ✅ **Expected:** Only recurring tasks shown (with 🔁 badge)
   - Change to "One-time Only"
   - ✅ **Expected:** Only non-recurring tasks shown

7. **Tags Filter**
   - In Tags input, type: `work, urgent`
   - Apply Filters
   - ✅ **Expected:** Only tasks with both "work" AND "urgent" tags shown

8. **Combined Filters**
   - Search: "project"
   - Priority: High, Urgent
   - Status: Pending
   - Due After: Today
   - Apply all at once
   - ✅ **Expected:** Results match ALL criteria (AND logic)
   - Active filters summary shows all active filters

9. **Clear Filters**
   - With filters active, click "Clear All"
   - ✅ **Expected:** All filters reset
   - All tasks shown again
   - Active filters summary disappears

10. **Results Summary**
    - Apply any filter combination
    - Check bottom of page
    - ✅ **Expected:** Message shows: "Showing X of Y total tasks"

### Success Criteria

- [ ] Advanced Search component visible and expandable
- [ ] All filter types work correctly
- [ ] Multiple filters combine properly (AND logic)
- [ ] Active filters display with colored badges
- [ ] Clear All resets everything
- [ ] Results count updates correctly
- [ ] Loading state shows during search
- [ ] No console errors during filtering

---

## Test 3: Backend Integration

### Objective
Verify frontend correctly communicates with backend API.

### Steps

1. **Check Network Requests**
   - Open DevTools → Network tab
   - Apply advanced search with filters
   - Look for request to `/api/tasks/search?...`
   - ✅ **Expected:** 
     - Status: 200 OK
     - Query params match filters (e.g., `priority=high&priority=urgent`)
     - Response contains filtered tasks array

2. **Verify Query Parameters**
   - Apply filters: Priority=High, Tags=work, Due After=2025-12-26
   - Check Network request URL
   - ✅ **Expected URL:**
     ```
     /api/tasks/search?priority=high&tags=work&due_after=2025-12-26T00:00
     ```

3. **Authentication Check**
   - Edit a task or search
   - Check request headers in Network tab
   - ✅ **Expected:** 
     - Authorization header present (or cookies sent)
     - No 401 Unauthorized errors

### Success Criteria

- [ ] API requests succeed (200 status)
- [ ] Query params correctly formatted
- [ ] Authentication works seamlessly
- [ ] Response data matches UI display

---

## Test 4: Regression Testing

### Objective
Ensure existing features still work after bug fixes.

### Steps

1. **Create New Task**
   - Click "+ New Task"
   - Fill out all fields
   - Save
   - ✅ **Expected:** Task appears in list

2. **Toggle Task Completion**
   - Click checkbox on pending task
   - ✅ **Expected:** Task marked complete with strikethrough
   - Click again
   - ✅ **Expected:** Task marked pending again

3. **Delete Task**
   - Click "Delete" on any task
   - Confirm deletion
   - ✅ **Expected:** Task removed from list

4. **Basic Filters**
   - Click "All", "Pending", "Completed" buttons
   - ✅ **Expected:** Status filter still works
   - Works independently from Advanced Search

5. **AI Chat (If Available)**
   - Open AI Chat
   - Ask: "Update my first task to high priority"
   - ✅ **Expected:** AI updates task
   - Verify manual edit also works on same task

6. **Stats Cards**
   - Check Total, Pending, Completed counts
   - Create/complete/delete tasks
   - ✅ **Expected:** Numbers update correctly

### Success Criteria

- [ ] All existing features work
- [ ] No regressions introduced
- [ ] UI remains responsive
- [ ] No new console errors

---

## Test 5: Edge Cases & Error Scenarios

### Objective
Test boundary conditions and error handling.

### Steps

1. **Empty Search Results**
   - Search for non-existent text: "xyzabc123"
   - ✅ **Expected:** "No tasks found" message
   - Helpful suggestion to adjust filters

2. **Invalid Date Range**
   - Set Due After = Jan 1, 2026
   - Set Due Before = Dec 1, 2025 (before "after" date)
   - Apply
   - ✅ **Expected:** No tasks shown OR validation error

3. **Network Failure Simulation**
   - Open DevTools → Network tab → Throttle to "Offline"
   - Try to edit a task
   - ✅ **Expected:** Error message displayed
   - Error should mention connection issue

4. **Long Task Titles**
   - Edit task with very long title (200+ characters)
   - ✅ **Expected:** Either truncated in UI or scrollable

5. **Special Characters**
   - Create task with title: `Test <script>alert('xss')</script>`
   - ✅ **Expected:** Renders as plain text (no script execution)
   - React auto-escapes HTML

6. **Multiple Simultaneous Edits**
   - Open edit form for task A
   - Don't save
   - Open edit form for task B
   - ✅ **Expected:** Task A edit cancels OR both can be edited

### Success Criteria

- [ ] No crashes on edge cases
- [ ] Errors handled gracefully
- [ ] User-friendly error messages
- [ ] No security vulnerabilities (XSS, etc.)

---

## 📊 Acceptance Criteria Summary

### Manual Task Edit Fix

| Requirement | Status | Notes |
|------------|--------|-------|
| Edit button opens form | ✅ ❌ | |
| Title updates correctly | ✅ ❌ | |
| Description updates | ✅ ❌ | |
| Priority updates with badge | ✅ ❌ | |
| Due date saves properly | ✅ ❌ | |
| Recurring toggle works | ✅ ❌ | |
| Frequency saves correctly | ✅ ❌ | |
| Error messages display | ✅ ❌ | |
| Loading state shows | ✅ ❌ | |
| No console errors | ✅ ❌ | |

### Advanced Search UI

| Requirement | Status | Notes |
|------------|--------|-------|
| Component visible | ✅ ❌ | |
| Text search works | ✅ ❌ | |
| Priority filter works | ✅ ❌ | |
| Status filter works | ✅ ❌ | |
| Date range filter works | ✅ ❌ | |
| Recurring filter works | ✅ ❌ | |
| Tags filter works | ✅ ❌ | |
| Combined filters (AND) | ✅ ❌ | |
| Active filters display | ✅ ❌ | |
| Clear all resets | ✅ ❌ | |
| Results count accurate | ✅ ❌ | |
| Loading state shows | ✅ ❌ | |

---

## 🐛 Bug Report Template

If you find issues during testing:

**Bug Title:** [Short description]

**Environment:**
- URL: http://34.93.106.63
- Version: 5.0.9
- Browser: [Chrome/Firefox/Safari] [Version]
- OS: [Windows/Mac/Linux]

**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Behavior:**


**Actual Behavior:**


**Screenshots/Console Errors:**


**Severity:** [Critical/High/Medium/Low]

---

## 🚀 Deployment Verification

### Before Marking as Complete

1. **Pods Running**
   ```bash
   kubectl get pods -n todo-app
   # Both todo-frontend pods should be Running
   ```

2. **Service Accessible**
   ```bash
   curl -I http://34.93.106.63
   # Should return 200 OK
   ```

3. **Image Version**
   ```bash
   kubectl describe deployment todo-frontend -n todo-app | grep Image
   # Should show: gcr.io/intense-optics-485323-f3/todo-frontend:5.0.9
   ```

4. **No Pod Errors**
   ```bash
   kubectl logs -n todo-app deployment/todo-frontend --tail=50
   # Check for any startup errors
   ```

---

## 📈 Performance Benchmarks

### Load Times (Target)

- Dashboard initial load: < 2s
- Task edit save: < 500ms
- Advanced search results: < 1s
- Task creation: < 500ms

### Monitoring

Check these metrics after deployment:
- CPU usage (should be < 50% per pod)
- Memory usage (should be < 200MB per pod)
- Response times (p95 < 1s)
- Error rate (should be < 1%)

---

## ✅ Final Checklist

### Deployment
- [x] Docker image built (5.0.9)
- [x] Image pushed to GCR
- [x] Kubernetes deployment updated
- [x] Pods rolled out successfully
- [x] Both pods running and healthy

### Testing
- [ ] Manual task edit verified
- [ ] Advanced search tested
- [ ] All filters working
- [ ] Error handling confirmed
- [ ] Regression tests passed
- [ ] Edge cases handled
- [ ] No console errors
- [ ] Performance acceptable

### Documentation
- [x] BUG-FIXES-v5.0.9.md created
- [x] TESTING-GUIDE-v5.0.9.md created
- [ ] README.md updated with bug fix notes
- [ ] PHASE5-SUBMISSION-README.md updated

### Communication
- [ ] Team notified of deployment
- [ ] Hackathon organizers informed (if needed)
- [ ] Demo video updated (optional)

---

## 🎓 Known Issues & Limitations

1. **Search is not real-time** - Must click "Apply Filters"
2. **Tag input is comma-separated** - No autocomplete yet
3. **Filters don't persist** - Reset on page refresh
4. **Date pickers are browser-dependent** - UI varies by browser

---

## 🔄 Rollback Procedure

If critical issues found:

```bash
# Rollback to previous version
kubectl set image deployment/todo-frontend \
  frontend=gcr.io/intense-optics-485323-f3/todo-frontend:5.0.8 \
  -n todo-app

# Verify rollback
kubectl rollout status deployment/todo-frontend -n todo-app
```

**Important:** Document any issues found before rolling back.

---

## 📞 Support Contacts

**For Testing Questions:**
- Check PHASE5-TESTING-GUIDE.md
- Review PHASE3-TESTING-GUIDE.md for AI Chat

**For Deployment Issues:**
- Check Kubernetes logs: `kubectl logs -n todo-app deployment/todo-frontend`
- Review backend logs: `kubectl logs -n todo-app deployment/todo-backend`

---

**Testing Status:** 🔄 Ready for Testing  
**Deployment Status:** ✅ Live on Production  
**Next Action:** Complete testing checklist above

---

**Happy Testing! 🎉**
