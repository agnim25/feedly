'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { feedsApi } from '@/lib/api'
import { useState } from 'react'

interface Feed {
  id: number
  name: string
  url: string
  feed_type: string
}

interface FeedListProps {
  selectedFeed: number | null
  onSelectFeed: (id: number | null) => void
  selectedCategory?: number | null
}

export default function FeedList({ selectedFeed, onSelectFeed, selectedCategory }: FeedListProps) {
  const [showAddForm, setShowAddForm] = useState(false)
  const [feedName, setFeedName] = useState('')
  const [feedUrl, setFeedUrl] = useState('')
  const [feedType, setFeedType] = useState('rss')
  const [twitterConfig, setTwitterConfig] = useState({ username: '', hashtag: '' })
  const queryClient = useQueryClient()

  const { data: feeds = [] } = useQuery({
    queryKey: ['feeds'],
    queryFn: feedsApi.getAll,
  })
  
  // Filter feeds by selected category
  // When a category is selected, show feeds in that category
  // When no category is selected, show all uncategorized feeds
  const filteredFeeds = selectedCategory 
    ? feeds.filter((feed: any) => feed.category_id === selectedCategory)
    : feeds  // Show all feeds when no category is selected (user can see all)

  const createMutation = useMutation({
    mutationFn: feedsApi.create,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['feeds'] })
      queryClient.invalidateQueries({ queryKey: ['items'] })  // Refresh items after RSS fetch
      setShowAddForm(false)
      setFeedName('')
      setFeedUrl('')
      setFeedType('rss')
      setTwitterConfig({ username: '', hashtag: '' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: feedsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feeds'] })
      if (selectedFeed) {
        onSelectFeed(null)
      }
    },
  })

  const fetchMutation = useMutation({
    mutationFn: feedsApi.fetch,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] })
    },
  })

  const handleAddFeed = async (e: React.FormEvent) => {
    e.preventDefault()
    if (feedName.trim() && (feedUrl.trim() || feedType === 'twitter')) {
      const config = feedType === 'twitter' 
        ? (twitterConfig.username ? { username: twitterConfig.username } : { hashtag: twitterConfig.hashtag })
        : {}
      
      createMutation.mutate({
        name: feedName.trim(),
        url: feedUrl.trim() || 'N/A',
        feed_type: feedType,
        config,
        category_id: selectedCategory || undefined,
      }, {
        onSuccess: () => {
          // Auto-fetch RSS feeds after creation
          if (feedType === 'rss') {
            // The backend will auto-fetch, but we can also invalidate items to refresh
            queryClient.invalidateQueries({ queryKey: ['items'] })
          }
        }
      })
    }
  }

  const handleDeleteFeed = (id: number) => {
    if (confirm('Are you sure you want to delete this feed?')) {
      deleteMutation.mutate(id)
    }
  }

  const handleFetchFeed = (id: number) => {
    fetchMutation.mutate(id)
  }

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-gray-700 uppercase">
          {selectedCategory ? 'Category Feeds' : 'Feeds'}
        </h2>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="text-indigo-600 hover:text-indigo-700 text-sm"
        >
          + Add
        </button>
      </div>
      
      {selectedCategory && (
        <div className="mb-2 text-xs text-gray-500 italic">
          Adding feed to this category
        </div>
      )}

      {showAddForm && (
        <form onSubmit={handleAddFeed} className="mb-4 space-y-2">
          <input
            type="text"
            value={feedName}
            onChange={(e) => setFeedName(e.target.value)}
            placeholder="Feed name"
            className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
            required
          />
          <select
            value={feedType}
            onChange={(e) => setFeedType(e.target.value)}
            className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
          >
            <option value="rss">RSS Feed</option>
            <option value="twitter">Twitter</option>
          </select>
          {feedType === 'rss' ? (
            <input
              type="url"
              value={feedUrl}
              onChange={(e) => setFeedUrl(e.target.value)}
              placeholder="RSS Feed URL"
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
              required
            />
          ) : (
            <div className="space-y-2">
              <input
                type="text"
                value={twitterConfig.username}
                onChange={(e) => setTwitterConfig({ ...twitterConfig, username: e.target.value, hashtag: '' })}
                placeholder="Twitter username (without @)"
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
              />
              <div className="text-xs text-gray-500 text-center">OR</div>
              <input
                type="text"
                value={twitterConfig.hashtag}
                onChange={(e) => setTwitterConfig({ ...twitterConfig, hashtag: e.target.value, username: '' })}
                placeholder="Hashtag (without #)"
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
              />
            </div>
          )}
          <div className="flex space-x-2">
            <button
              type="submit"
              className="flex-1 px-2 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700"
            >
              Add
            </button>
            <button
              type="button"
              onClick={() => {
                setShowAddForm(false)
                setFeedName('')
                setFeedUrl('')
                setFeedType('rss')
                setTwitterConfig({ username: '', hashtag: '' })
              }}
              className="flex-1 px-2 py-1 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="space-y-1">
        {filteredFeeds.length === 0 ? (
          <div className="text-sm text-gray-500 py-2">
            {selectedCategory ? 'No feeds in this category' : 'No feeds yet'}
          </div>
        ) : (
          filteredFeeds.map((feed: Feed) => (
            <div
              key={feed.id}
              className={`group px-3 py-2 rounded hover:bg-gray-100 ${
                selectedFeed === feed.id ? 'bg-indigo-50' : ''
              }`}
            >
              <div className="flex items-center justify-between">
                <button
                  onClick={() => onSelectFeed(feed.id === selectedFeed ? null : feed.id)}
                  className="flex-1 text-left text-sm text-gray-700"
                >
                  {feed.name}
                </button>
                <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => handleFetchFeed(feed.id)}
                    className="text-xs text-indigo-600 hover:text-indigo-700"
                    title="Fetch now"
                  >
                    ↻
                  </button>
                  <button
                    onClick={() => handleDeleteFeed(feed.id)}
                    className="text-xs text-red-600 hover:text-red-700"
                    title="Delete"
                  >
                    ×
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {selectedFeed && (
        <button
          onClick={() => onSelectFeed(null)}
          className="mt-4 w-full px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded"
        >
          Show All
        </button>
      )}
    </div>
  )
}

