'use client'

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { itemsApi } from '@/lib/api'
import { format } from 'date-fns'
import { useState } from 'react'
import CategoryAssignment from './CategoryAssignment'

interface FeedItemProps {
  item: {
    id: number
    title: string
    content: string | null
    url: string
    published_at: string | null
    read_at: string | null
    feed_id: number
  }
}

export default function FeedItem({ item }: FeedItemProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const queryClient = useQueryClient()

  const markReadMutation = useMutation({
    mutationFn: () => itemsApi.markRead(item.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] })
    },
  })

  const markUnreadMutation = useMutation({
    mutationFn: () => itemsApi.markUnread(item.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] })
    },
  })

  const isRead = !!item.read_at

  const handleToggleRead = () => {
    if (isRead) {
      markUnreadMutation.mutate()
    } else {
      markReadMutation.mutate()
    }
  }

  return (
    <div className={`bg-white rounded-lg border ${isRead ? 'border-gray-200' : 'border-indigo-200'} shadow-sm hover:shadow-md transition-shadow`}>
      <div className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className={`text-lg font-semibold mb-2 ${isRead ? 'text-gray-600' : 'text-gray-900'}`}>
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-indigo-600"
              >
                {item.title}
              </a>
            </h3>
            {item.published_at && (
              <p className="text-sm text-gray-500 mb-2">
                {format(new Date(item.published_at), 'MMM d, yyyy h:mm a')}
              </p>
            )}
            {item.content && (
              <div className={`text-gray-700 ${isExpanded ? '' : 'line-clamp-3'}`}>
                <div dangerouslySetInnerHTML={{ __html: item.content }} />
              </div>
            )}
            {item.content && item.content.length > 150 && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-sm text-indigo-600 hover:text-indigo-700 mt-2"
              >
                {isExpanded ? 'Show less' : 'Show more'}
              </button>
            )}
          </div>
          <div className="ml-4 flex flex-col space-y-2">
            <button
              onClick={handleToggleRead}
              className={`px-3 py-1 text-xs rounded ${
                isRead
                  ? 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  : 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200'
              }`}
            >
              {isRead ? 'Read' : 'Unread'}
            </button>
          </div>
        </div>
        <div className="mt-3 pt-3 border-t border-gray-200 flex items-center justify-between">
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-indigo-600 hover:text-indigo-700"
          >
            Read full article →
          </a>
          <CategoryAssignment itemId={item.id} />
        </div>
      </div>
    </div>
  )
}

