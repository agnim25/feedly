'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { itemsApi } from '@/lib/api'
import FeedItem from '@/components/FeedItem'
import CategoryTree from '@/components/CategoryTree'
import FeedList from '@/components/FeedList'

export default function DashboardPage() {
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null)
  const [selectedFeed, setSelectedFeed] = useState<number | null>(null)
  const [unreadOnly, setUnreadOnly] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [sinceDate, setSinceDate] = useState<string>('')

  const { data: items = [], isLoading } = useQuery({
    queryKey: ['items', selectedCategory, selectedFeed, unreadOnly, sinceDate],
    queryFn: () => itemsApi.getAll({
      category_id: selectedCategory || undefined,
      feed_id: selectedFeed || undefined,
      unread_only: unreadOnly,
      since_date: sinceDate || undefined,
    }),
  })

  const filteredItems = items.filter((item: any) => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    return (
      item.title.toLowerCase().includes(query) ||
      (item.content && item.content.toLowerCase().includes(query))
    )
  })

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">Feedly</h1>
        </div>
        <div className="flex-1 overflow-y-auto">
          <CategoryTree
            selectedCategory={selectedCategory}
            onSelectCategory={setSelectedCategory}
          />
          <div className="border-t border-gray-200 mt-4">
            <FeedList
              selectedFeed={selectedFeed}
              onSelectFeed={setSelectedFeed}
              selectedCategory={selectedCategory}
            />
          </div>
        </div>
        <div className="p-4 border-t border-gray-200 space-y-3">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={unreadOnly}
              onChange={(e) => setUnreadOnly(e.target.checked)}
              className="rounded border-gray-300"
            />
            <span className="text-sm text-gray-700">Unread only</span>
          </label>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto flex flex-col">
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {selectedCategory ? 'Category Items' : selectedFeed ? 'Feed Items' : 'All Items'}
                </h2>
                {items.length > 0 && (
                  <p className="text-sm text-gray-500 mt-1">
                    {filteredItems.length} {filteredItems.length === 1 ? 'item' : 'items'}
                    {sinceDate && ` since ${sinceDate}`}
                  </p>
                )}
              </div>
            </div>
            <div className="flex space-x-2">
              <input
                type="text"
                placeholder="Search items..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <input
                type="date"
                placeholder="Since date"
                value={sinceDate}
                onChange={(e) => setSinceDate(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                title="Show items since this date"
              />
              {sinceDate && (
                <button
                  onClick={() => setSinceDate('')}
                  className="px-3 py-2 text-sm text-gray-600 hover:text-gray-900"
                  title="Clear date filter"
                >
                  ✕
                </button>
              )}
            </div>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto p-6">
            {isLoading ? (
              <div className="text-center py-12">
                <div className="text-gray-500">Loading...</div>
              </div>
            ) : filteredItems.length > 0 ? (
              <div className="space-y-4">
                {filteredItems.map((item: any) => (
                  <FeedItem key={item.id} item={item} />
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="text-gray-500">
                  {searchQuery ? 'No items match your search' : 'No items found'}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
