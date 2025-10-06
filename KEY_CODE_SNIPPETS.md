# Key Code Snippets - Frontend Redesign

## 1. Article Types (`/frontend/src/types/article.ts`)

```typescript
export interface Article {
  id: string
  user_id: number
  headline: string
  url: string | null
  category: string
  received_date: string
  position: number
  created_at: string
  updated_at: string
  source_count: number  // Number of newsletters this article appeared in
}

export interface ArticlesByCategory {
  category: string
  article_count: number
  articles: Article[]
}
```

## 2. Article Service (`/frontend/src/services/articleService.ts`)

```typescript
class ArticleService {
  async getRecent(limit: number = 100, groupByCategory: boolean = false) {
    const params = { limit }
    
    if (groupByCategory) {
      params.group_by_category = true
      const response = await apiClient.get<ArticlesByCategoryResponse>('/articles/recent', { params })
      return response.data.categories  // ArticlesByCategory[]
    } else {
      const response = await apiClient.get<ArticleListResponse>('/articles/recent', { params })
      return response.data.articles  // Article[]
    }
  }
  
  async search(query: string, limit = 50, offset = 0) {
    const params = { query, limit, offset }
    const response = await apiClient.get<ArticleSearchResponse>('/articles/search', { params })
    return response.data.articles
  }
}
```

## 3. Article Item Component (`/frontend/src/components/articles/ArticleItem.tsx`)

```typescript
export function ArticleItem({ article, showBookmark = true }) {
  const { id, headline, url } = article

  return (
    <div className="group flex items-center justify-between gap-4 py-3 px-4 
                    rounded-lg transition-all hover:bg-accent/50">
      <div className="flex-1 min-w-0">
        {url ? (
          <a href={url} target="_blank" rel="noopener noreferrer" 
             className="flex items-center gap-2 group/link">
            <span className="text-sm font-medium line-clamp-2 
                           group-hover/link:text-primary">
              {headline}
            </span>
            <ExternalLink className="h-3.5 w-3.5 opacity-0 group-hover:opacity-100" />
          </a>
        ) : (
          <span className="text-sm font-medium">{headline}</span>
        )}
      </div>

      {showBookmark && (
        <div className="opacity-0 group-hover:opacity-100">
          <BookmarkButton articleId={id} size="sm" />
        </div>
      )}
    </div>
  )
}
```

## 4. Newsstand Page Structure (`/frontend/src/pages/Newsstand.tsx`)

```typescript
export function Newsstand() {
  const [categories, setCategories] = useState<ArticlesByCategory[]>([])
  
  useEffect(() => {
    const loadArticles = async () => {
      const data = await articleService.getRecent(100, true) as ArticlesByCategory[]
      setCategories(data)
    }
    loadArticles()
  }, [])

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header with Fetch Button */}
        <div className="flex items-center justify-between">
          <h1>Newsstand</h1>
          <Button onClick={handleFetchNewsletters}>Fetch Newsletters</Button>
        </div>

        {/* Articles by Category - Accordion */}
        <Accordion type="multiple" defaultValue={categories.map(cat => cat.category)}>
          {categories.map((category) => (
            <Card key={category.category}>
              <AccordionItem value={category.category}>
                <AccordionTrigger>
                  <div className="flex items-center justify-between w-full">
                    <span>{category.category}</span>
                    <Badge>{category.article_count} articles</Badge>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <ArticleList articles={category.articles} />
                </AccordionContent>
              </AccordionItem>
            </Card>
          ))}
        </Accordion>
      </div>
    </Layout>
  )
}
```

## 5. Updated Bookmark Button (`/frontend/src/components/bookmarks/BookmarkButton.tsx`)

```typescript
export function BookmarkButton({ articleId, variant = 'ghost', size = 'sm' }) {
  const [bookmarkedListIds, setBookmarkedListIds] = useState<Set<string>>(new Set())

  const loadLists = async () => {
    const allLists = await bookmarkService.getLists()
    
    // Check which lists contain this article
    const containingListIds = []
    for (const list of allLists) {
      const articles = await bookmarkService.getArticlesInList(list.id)
      if (articles.some(a => a.id === articleId)) {
        containingListIds.push(list.id)
      }
    }
    setBookmarkedListIds(new Set(containingListIds))
  }

  const handleToggleBookmark = async (listId: string, isBookmarked: boolean) => {
    if (isBookmarked) {
      await bookmarkService.removeArticleFromList(listId, articleId)
      // Update count optimistically
      setLists(prev => prev.map(list =>
        list.id === listId
          ? { ...list, article_count: Math.max(0, list.article_count - 1) }
          : list
      ))
    } else {
      await bookmarkService.addArticleToList(listId, articleId)
      setLists(prev => prev.map(list =>
        list.id === listId
          ? { ...list, article_count: list.article_count + 1 }
          : list
      ))
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant={variant} size={size}>
          <Bookmark className={cn(isBookmarked && "fill-current")} />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        {/* List items with checkboxes */}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

## 6. Updated Bookmarks Page (`/frontend/src/pages/Bookmarks.tsx`)

```typescript
export function Bookmarks() {
  const [articles, setArticles] = useState<ArticleInBookmark[]>([])
  
  const loadArticles = async (listId: string) => {
    const data = await bookmarkService.getArticlesInList(listId)
    setArticles(data)
  }

  return (
    <Layout>
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Sidebar - List Manager */}
        <BookmarkListManager 
          selectedListId={selectedListId}
          onSelectList={setSelectedListId}
        />

        {/* Main Content - Articles */}
        <div className="lg:col-span-2">
          {articles.length === 0 ? (
            <Card>
              <CardContent>
                <p>No articles saved yet</p>
                <p>Click the bookmark button on any article to add it to this list</p>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent>
                <ArticleList articles={articles} showBookmark={false} />
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </Layout>
  )
}
```

## 7. Accordion Component (`/frontend/src/components/ui/accordion.tsx`)

```typescript
import * as AccordionPrimitive from "@radix-ui/react-accordion"

const AccordionTrigger = React.forwardRef(({ children, ...props }, ref) => (
  <AccordionPrimitive.Header className="flex">
    <AccordionPrimitive.Trigger
      ref={ref}
      className="flex flex-1 items-center justify-between py-4 
                 hover:underline [&[data-state=open]>svg]:rotate-180"
      {...props}
    >
      {children}
      <ChevronDown className="h-4 w-4 transition-transform duration-200" />
    </AccordionPrimitive.Trigger>
  </AccordionPrimitive.Header>
))

const AccordionContent = React.forwardRef(({ children, ...props }, ref) => (
  <AccordionPrimitive.Content
    ref={ref}
    className="overflow-hidden 
               data-[state=closed]:animate-accordion-up 
               data-[state=open]:animate-accordion-down"
    {...props}
  >
    <div className="pb-4 pt-0">{children}</div>
  </AccordionPrimitive.Content>
))
```

## 8. Updated Routing (`/frontend/src/App.tsx`)

```typescript
import { Newsstand } from '@/pages/Newsstand'  // Changed from Newsletters

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/newsstand" element={<ProtectedRoute><Newsstand /></ProtectedRoute>} />
        <Route path="/bookmarks" element={<ProtectedRoute><Bookmarks /></ProtectedRoute>} />
        <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  )
}
```

## 9. Updated Navigation (`/frontend/src/components/layout/Navigation.tsx`)

```typescript
const navItems: NavItem[] = [
  { icon: LayoutDashboard, label: 'Overview', href: '/', isRoute: true },
  { icon: TrendingUp, label: 'Metrics', href: '#metrics' },
  { icon: Newspaper, label: 'Breaking News', href: '#breaking' },
  { icon: Calendar, label: 'Weekly Summary', href: '#weekly' },
  { icon: BookOpen, label: 'Newsstand', href: '/newsstand', isRoute: true },  // Changed
  { icon: Bookmark, label: 'Bookmarks', href: '/bookmarks', isRoute: true },
  { icon: Settings, label: 'Settings', href: '/settings', isRoute: true },
]
```

## 10. Article List with Animations (`/frontend/src/components/articles/ArticleList.tsx`)

```typescript
export function ArticleList({ articles, showBookmark = true }) {
  if (articles.length === 0) {
    return (
      <div className="py-8 text-center">
        <p className="text-sm text-muted-foreground">No articles available</p>
      </div>
    )
  }

  return (
    <div className="space-y-1">
      {articles.map((article, index) => (
        <div
          key={article.id}
          className="animate-slide-up"
          style={{ animationDelay: `${index * 30}ms` }}
        >
          <ArticleItem article={article} showBookmark={showBookmark} />
        </div>
      ))}
    </div>
  )
}
```

## API Contract Expected by Frontend

### Article Endpoints
```
GET  /articles/recent?limit=100&group_by_category=true
→ { categories: [{ category, article_count, articles: [...] }], total_articles }

GET  /articles/recent?limit=100
→ { articles: [...], count }

GET  /articles/by-category?category=Texas%20Tea&limit=50&offset=0
→ { articles: [...], count }

GET  /articles/search?query=houston&limit=50&offset=0
→ { articles: [...], count, total_count, query }

GET  /articles/{id}
→ { id, headline, url, category, ..., newsletter_subjects: [...] }
```

### Bookmark Endpoints (Updated)
```
GET    /bookmarks/lists
→ { lists: [{ id, name, article_count, created_at, updated_at }] }

POST   /bookmarks/lists/{listId}/articles/{articleId}
→ 201 Created

DELETE /bookmarks/lists/{listId}/articles/{articleId}
→ 204 No Content

GET    /bookmarks/lists/{listId}/articles
→ { articles: [{ ...article, bookmarked_at }] }
```

## Design Patterns Used

### 1. Optimistic UI Updates
- Bookmark counts update immediately
- Revert on error

### 2. Staggered Animations
- Articles fade in with delays: `${index * 30}ms`
- Smooth, sequential appearance

### 3. Hover-based Actions
- Bookmark button appears on article hover
- Reduces visual clutter

### 4. Type-safe Services
- All API calls return typed responses
- Explicit error handling

### 5. Component Composition
- ArticleItem (atom)
- ArticleList (molecule)
- Newsstand (organism/page)
