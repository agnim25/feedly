'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { categoriesApi, feedsApi } from '@/lib/api'
import { useState } from 'react'

interface Category {
  id: number
  name: string
  parent_id: number | null
  children: Category[]
}

interface CategoryTreeProps {
  selectedCategory: number | null
  onSelectCategory: (id: number | null) => void
}

function CategoryNode({ category, selectedCategory, onSelect, level = 0, feeds = [] }: {
  category: Category
  selectedCategory: number | null
  onSelect: (id: number) => void
  level?: number
  feeds?: any[]
}) {
  const isSelected = selectedCategory === category.id
  const categoryFeeds = feeds.filter((f: any) => f.category_id === category.id)

  return (
    <div>
      <div
        onClick={() => onSelect(category.id)}
        className={`px-3 py-2 cursor-pointer hover:bg-gray-100 rounded ${
          isSelected ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700'
        }`}
        style={{ paddingLeft: `${12 + level * 16}px` }}
      >
        <div className="flex items-center justify-between">
          <span className="text-sm">{category.name}</span>
          {categoryFeeds.length > 0 && (
            <span className="text-xs text-gray-500 ml-2">({categoryFeeds.length})</span>
          )}
        </div>
      </div>
      {category.children && category.children.length > 0 && (
        <div>
          {category.children.map((child) => (
            <CategoryNode
              key={child.id}
              category={child}
              selectedCategory={selectedCategory}
              onSelect={onSelect}
              level={level + 1}
              feeds={feeds}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default function CategoryTree({ selectedCategory, onSelectCategory }: CategoryTreeProps) {
  const [showAddForm, setShowAddForm] = useState(false)
  const [newCategoryName, setNewCategoryName] = useState('')
  const [parentId, setParentId] = useState<number | null>(null)
  const queryClient = useQueryClient()

  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: categoriesApi.getAll,
  })
  
  const { data: feeds = [] } = useQuery({
    queryKey: ['feeds'],
    queryFn: feedsApi.getAll,
  })

  const createMutation = useMutation({
    mutationFn: categoriesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] })
      setShowAddForm(false)
      setNewCategoryName('')
      setParentId(null)
    },
  })

  const handleAddCategory = (e: React.FormEvent) => {
    e.preventDefault()
    if (newCategoryName.trim()) {
      createMutation.mutate({
        name: newCategoryName.trim(),
        parent_id: parentId || undefined,
      })
    }
  }

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-gray-700 uppercase">Categories</h2>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="text-indigo-600 hover:text-indigo-700 text-sm"
        >
          + Add
        </button>
      </div>

      {showAddForm && (
        <form onSubmit={handleAddCategory} className="mb-4">
          <input
            type="text"
            value={newCategoryName}
            onChange={(e) => setNewCategoryName(e.target.value)}
            placeholder="Category name"
            className="w-full px-2 py-1 text-sm border border-gray-300 rounded mb-2"
            autoFocus
          />
          <select
            value={parentId || ''}
            onChange={(e) => setParentId(e.target.value ? parseInt(e.target.value) : null)}
            className="w-full px-2 py-1 text-sm border border-gray-300 rounded mb-2"
          >
            <option value="">No parent</option>
            {categories.map((cat: Category) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
          <div className="flex space-x-2">
            <button
              type="submit"
              className="flex-1 px-2 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700"
            >
              Create
            </button>
            <button
              type="button"
              onClick={() => {
                setShowAddForm(false)
                setNewCategoryName('')
                setParentId(null)
              }}
              className="flex-1 px-2 py-1 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div>
        {categories.length === 0 ? (
          <div className="text-sm text-gray-500 py-2">No categories yet</div>
        ) : (
          categories.map((category: Category) => (
            <CategoryNode
              key={category.id}
              category={category}
              selectedCategory={selectedCategory}
              onSelect={onSelectCategory}
              feeds={feeds || []}
            />
          ))
        )}
      </div>

      {selectedCategory && (
        <button
          onClick={() => onSelectCategory(null)}
          className="mt-4 w-full px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded"
        >
          Show All
        </button>
      )}
    </div>
  )
}

