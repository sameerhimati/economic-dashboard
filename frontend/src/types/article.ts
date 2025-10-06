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
  newsletter_subjects: string[]  // Subjects of newsletters containing this article
}

export interface ArticlesByCategory {
  category: string
  article_count: number
  articles: Article[]
}
