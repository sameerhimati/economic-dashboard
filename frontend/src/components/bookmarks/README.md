# Bookmark Lists System

A comprehensive system for organizing newsletters into custom bookmark lists.

## Features

- **Create & Manage Lists**: Create up to 10 custom bookmark lists with unique names
- **Quick Save**: Save newsletters to lists with a single click using the bookmark button
- **Visual Feedback**: Filled bookmark icon indicates saved newsletters
- **Optimistic Updates**: Instant UI updates for seamless user experience
- **List Organization**: View all lists with newsletter counts and last updated timestamps
- **Dedicated Page**: Full-page bookmarks view with sidebar navigation

## Components

### BookmarkButton
A dropdown button component that allows users to quickly save/remove newsletters from bookmark lists.

**Props:**
- `newsletterId: string` - The ID of the newsletter to bookmark
- `variant?: 'default' | 'ghost' | 'outline'` - Button variant (default: 'ghost')
- `size?: 'default' | 'sm' | 'lg' | 'icon'` - Button size (default: 'sm')
- `className?: string` - Additional CSS classes
- `onCreateList?: () => void` - Callback when "Create List" is clicked

**Usage:**
```tsx
import { BookmarkButton } from '@/components/bookmarks/BookmarkButton'

<BookmarkButton
  newsletterId={newsletter.id}
  variant="ghost"
  size="sm"
/>
```

**Features:**
- Shows all user's bookmark lists in dropdown
- Checkboxes indicate which lists contain the newsletter
- Click to toggle add/remove
- Loading states for async operations
- Empty state with "Create List" option
- Visual feedback (filled icon when bookmarked)

### BookmarkListManager
A comprehensive component for managing bookmark lists.

**Props:**
- `selectedListId?: string` - Currently selected list ID
- `onSelectList?: (listId: string | null) => void` - Callback when list is selected
- `compact?: boolean` - Use compact layout (default: false)

**Usage:**
```tsx
import { BookmarkListManager } from '@/components/bookmarks/BookmarkListManager'

<BookmarkListManager
  selectedListId={selectedListId}
  onSelectList={handleSelectList}
/>
```

**Features:**
- Create new lists (up to 10)
- Rename existing lists
- Delete lists with confirmation
- Show newsletter count per list
- Empty state guidance
- Inline editing
- Optimistic updates

## Pages

### Bookmarks Page
Full-page view for managing bookmarks at `/bookmarks`.

**Features:**
- Sidebar with BookmarkListManager
- Main content area showing selected list's newsletters
- Empty states for no lists or no newsletters
- Smooth animations
- Responsive layout

**Usage:**
Navigate to `/bookmarks` or click "Bookmarks" in the navigation menu.

## Service

### bookmarkService
API service for all bookmark operations.

**Methods:**
- `getLists()` - Get all bookmark lists
- `createList(name)` - Create new list
- `updateList(listId, name)` - Rename list
- `deleteList(listId)` - Delete list
- `addNewsletterToList(listId, newsletterId)` - Add newsletter
- `removeNewsletterFromList(listId, newsletterId)` - Remove newsletter
- `getNewslettersInList(listId)` - Get list newsletters
- `getListsContainingNewsletter(newsletterId)` - Helper to check membership

## Error Handling

The system handles these specific cases:
- **400 (Max lists)**: "Maximum 10 bookmark lists reached"
- **409 (Duplicate name)**: "A list with this name already exists"
- **404 (Not found)**: "List not found" or "List or newsletter not found"
- **Network errors**: Generic error messages

All errors trigger toast notifications for user feedback.

## Integration

### NewsletterCard Integration
The BookmarkButton is integrated into every NewsletterCard in the header area, next to the expand/collapse button.

### Navigation
A "Bookmarks" link is added to the main navigation menu with a bookmark icon.

### Routing
The bookmarks page is protected and requires authentication.

## API Endpoints

All endpoints are prefixed with `/bookmarks`:

- `GET /bookmarks/lists` - Get user's lists
- `POST /bookmarks/lists` - Create list
- `PUT /bookmarks/lists/{id}` - Update list
- `DELETE /bookmarks/lists/{id}` - Delete list
- `POST /bookmarks/lists/{id}/newsletters/{nid}` - Add newsletter
- `DELETE /bookmarks/lists/{id}/newsletters/{nid}` - Remove newsletter
- `GET /bookmarks/lists/{id}/newsletters` - Get newsletters in list

## TypeScript Types

```typescript
interface BookmarkList {
  id: string
  name: string
  newsletter_count: number
  created_at: string
  updated_at: string
}

interface NewsletterInBookmark extends Newsletter {
  bookmarked_at: string
}
```

## Styling

The components use:
- Shadcn/ui components (Dialog, DropdownMenu, Card, Button, etc.)
- Tailwind CSS for styling
- Custom animations from the design system
- Consistent color scheme and spacing
- Responsive design patterns

## Accessibility

- Keyboard navigation support
- ARIA labels for screen readers
- Focus management in dialogs
- Semantic HTML structure
- Color contrast compliance
