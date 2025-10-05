# Newsletter Cleanup Endpoint

## Overview
The newsletter cleanup endpoint automatically deletes newsletters older than 7 days that are not saved in any bookmark list.

## Endpoint Details

**POST** `/newsletters/cleanup`

### Authentication
- **Required:** Yes
- Uses `get_current_active_user` dependency
- Only deletes newsletters belonging to the authenticated user

### Request
No request body or query parameters required.

### Response
```json
{
  "status": "success",
  "deleted_count": 5,
  "timestamp": "2025-10-05T12:00:00.000000+00:00"
}
```

### Response Schema
- `status` (string): Operation status ("success")
- `deleted_count` (integer): Number of newsletters deleted
- `timestamp` (string): ISO 8601 timestamp of operation

## Business Logic

### Deletion Criteria
A newsletter is deleted if ALL of the following conditions are met:

1. **User Ownership**: `user_id = current_user.id`
2. **Age**: `received_date < (NOW - 7 days)`
3. **Not Bookmarked**: Newsletter ID is NOT in any bookmark list

### Query Implementation

```python
# Find newsletters to delete
DELETE FROM newsletters
WHERE user_id = {current_user_id}
  AND received_date < NOW() - INTERVAL '7 days'
  AND id NOT IN (
    SELECT DISTINCT newsletter_id
    FROM newsletter_bookmarks
  )
```

### Safety Features

1. **User-Scoped**: Only operates on authenticated user's newsletters
2. **Bookmark Protection**: Preserves all bookmarked newsletters regardless of age
3. **Transaction Safety**: Uses database transactions with rollback on error
4. **Logging**: Comprehensive logging at all stages:
   - Cleanup start with user ID
   - Cutoff date calculation
   - Count of newsletters found
   - Count of newsletters deleted
   - Error logging with full traceback

## Error Handling

### HTTP Status Codes
- `200 OK`: Successful cleanup
- `401 Unauthorized`: User not authenticated
- `500 Internal Server Error`: Database or other errors

### Error Response
```json
{
  "detail": "Error cleaning up newsletters: {error_message}"
}
```

### Rollback Behavior
- Any database error triggers an automatic rollback
- No partial deletions occur
- Full error context logged for debugging

## Usage Examples

### Using cURL
```bash
curl -X POST "http://localhost:8000/newsletters/cleanup" \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json"
```

### Using Python requests
```python
import requests

response = requests.post(
    "http://localhost:8000/newsletters/cleanup",
    headers={"Authorization": f"Bearer {access_token}"}
)

result = response.json()
print(f"Deleted {result['deleted_count']} newsletters")
```

### Using JavaScript/fetch
```javascript
const response = await fetch('/newsletters/cleanup', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});

const result = await response.json();
console.log(`Deleted ${result.deleted_count} newsletters`);
```

## Testing Scenarios

### Test Case 1: Old Unbookmarked Newsletters
**Given:**
- User has 10 newsletters older than 7 days
- None are bookmarked

**Expected Result:**
- `deleted_count: 10`
- All 10 newsletters deleted

### Test Case 2: Old Bookmarked Newsletters
**Given:**
- User has 10 newsletters older than 7 days
- 3 are bookmarked

**Expected Result:**
- `deleted_count: 7`
- Only unbookmarked newsletters deleted
- Bookmarked newsletters preserved

### Test Case 3: Recent Newsletters
**Given:**
- User has 5 newsletters newer than 7 days
- None are bookmarked

**Expected Result:**
- `deleted_count: 0`
- No newsletters deleted (too recent)

### Test Case 4: Mixed Age and Bookmarks
**Given:**
- 5 newsletters > 7 days old, 2 bookmarked
- 5 newsletters < 7 days old, 1 bookmarked

**Expected Result:**
- `deleted_count: 3`
- Only old unbookmarked newsletters deleted
- All recent and bookmarked newsletters preserved

## Logging Output

### Successful Cleanup
```
INFO: Starting newsletter cleanup for user 123
INFO: Cleanup cutoff date: 2025-09-28T12:00:00.000000+00:00 for user 123
INFO: Found 5 newsletters to delete for user 123
INFO: Successfully deleted 5 newsletters for user 123
```

### No Newsletters to Delete
```
INFO: Starting newsletter cleanup for user 123
INFO: Cleanup cutoff date: 2025-09-28T12:00:00.000000+00:00 for user 123
INFO: Found 0 newsletters to delete for user 123
INFO: No newsletters to delete for user 123
```

### Error Scenario
```
INFO: Starting newsletter cleanup for user 123
INFO: Cleanup cutoff date: 2025-09-28T12:00:00.000000+00:00 for user 123
ERROR: Error during newsletter cleanup for user 123: Database connection failed
Traceback (most recent call last):
  ...
```

## Database Schema Reference

### Relevant Tables

**newsletters**
- `id` (UUID): Primary key
- `user_id` (Integer): Foreign key to users table
- `received_date` (DateTime): When email was received
- Other fields...

**newsletter_bookmarks**
- `newsletter_id` (UUID): Foreign key to newsletters
- `bookmark_list_id` (UUID): Foreign key to bookmark_lists
- `created_at` (DateTime): When bookmarked

**bookmark_lists**
- `id` (UUID): Primary key
- `user_id` (Integer): Foreign key to users table
- `name` (String): List name

### Relationships
- A newsletter can be in multiple bookmark lists (many-to-many)
- A bookmark list can contain multiple newsletters (many-to-many)
- Junction table: `newsletter_bookmarks`

## Integration Notes

### Frontend Integration
1. Add cleanup button to newsletter management UI
2. Call endpoint on user action (e.g., "Clean Up Old Newsletters")
3. Display confirmation dialog before cleanup
4. Show success message with deleted count
5. Refresh newsletter list after cleanup

### Scheduled Cleanup (Future Enhancement)
For automated cleanup, consider:
1. Background task scheduler (Celery, APScheduler)
2. Daily/weekly cleanup job
3. User preferences for cleanup frequency
4. Email notification of cleanup results

## Performance Considerations

### Query Optimization
- Uses subquery with DISTINCT for bookmarked newsletters
- Indexes on:
  - `newsletters.user_id`
  - `newsletters.received_date`
  - `newsletter_bookmarks.newsletter_id`

### Scalability
- Query executes in two steps:
  1. SELECT to get count (for logging)
  2. DELETE with same conditions
- For large datasets, consider batch deletion
- Monitor query performance with EXPLAIN

### Connection Pooling
- Uses async database session
- Automatic connection management
- Transaction handling with commit/rollback

## Security Considerations

1. **Authentication Required**: Endpoint requires valid JWT token
2. **User Isolation**: Only operates on authenticated user's data
3. **No User Input**: No user parameters to sanitize (reduces injection risk)
4. **Parameterized Queries**: Uses SQLAlchemy's query builder
5. **Transaction Safety**: Rollback on any error prevents data corruption

## Monitoring and Alerts

### Metrics to Track
- Number of newsletters deleted per user
- Frequency of cleanup calls
- Error rate
- Execution time

### Recommended Alerts
- Alert if error rate > 5%
- Alert if execution time > 5 seconds
- Alert if single cleanup deletes > 1000 newsletters (anomaly detection)

## Code Quality Checklist

✅ **Error Handling**
- Comprehensive try-except blocks
- Specific error messages
- Database rollback on failure

✅ **Logging**
- Startup, processing, completion logs
- Error logs with full traceback
- Structured logging with extra context

✅ **Type Safety**
- Type hints on all parameters
- Pydantic response model
- SQLAlchemy typed queries

✅ **Documentation**
- Clear docstring with purpose
- Parameter documentation
- Return type documentation
- Exception documentation

✅ **Security**
- Authentication required
- User-scoped operations
- No SQL injection vulnerabilities

✅ **Best Practices**
- Async/await for database operations
- Transaction management
- Proper HTTP status codes
- RESTful endpoint design
