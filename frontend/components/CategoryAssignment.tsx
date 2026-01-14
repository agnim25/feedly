'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { categoriesApi, itemsApi } from '@/lib/api'
import { useState } from 'react'

interface CategoryAssignmentProps {
  itemId: number
}

export default function CategoryAssignment({ itemId }: CategoryAssignmentProps) {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()

  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: categoriesApi.getAll,
  })

  const { data: currentCategories = [] } = useQuery({
    queryKey: ['item-categories', itemId],
    queryFn: () => itemsApi.getCategories(itemId),
  })

  const assignMutation = useMutation({
    mutationFn: ({ categoryId, itemId }: { categoryId: number; itemId: number }) =>
      categoriesApi.assignItem(categoryId, itemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] })
      queryClient.invalidateQueries({ queryKey: ['item-categories', itemId] })
    },
  })

  const flattenCategories = (cats: any[], result: any[] = [], level = 0): any[] => {
    for (const cat of cats) {
      result.push({ ...cat, level })
      if (cat.children && cat.children.length > 0) {
        flattenCategories(cat.children, result, level + 1)
      }
    }
    return result
  }

  const allCategories = flattenCategories(categories)

  const handleToggleCategory = (categoryId: number) => {
    const isAssigned = currentCategories.includes(categoryId)
    if (!isAssigned) {
      assignMutation.mutate({ categoryId, itemId })
    }
    // Note: Removing assignments would require the assignment ID
    // For now, we only allow adding assignments
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="text-sm text-indigo-600 hover:text-indigo-700"
      >
        Assign to category
      </button>
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute z-20 mt-2 w-64 bg-white rounded-md shadow-lg border border-gray-200">
            <div className="p-2 border-b border-gray-200">
              <h3 className="text-sm font-semibold text-gray-700">Assign to category</h3>
            </div>
            <div className="max-h-60 overflow-y-auto p-2">
              {allCategories.length === 0 ? (
                <div className="text-sm text-gray-500 py-2">No categories</div>
              ) : (
                allCategories.map((category: any) => {
                  const isAssigned = currentCategories.includes(category.id)
                  return (
                    <button
                      key={category.id}
                      onClick={() => {
                        handleToggleCategory(category.id)
                        if (!isAssigned) {
                          setIsOpen(false)
                        }
                      }}
                      className={`w-full text-left px-3 py-2 text-sm rounded hover:bg-gray-100 ${
                        isAssigned ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700'
                      }`}
                      style={{ paddingLeft: `${12 + category.level * 16}px` }}
                    >
                      {category.name} {isAssigned && '✓'}
                    </button>
                  )
                })
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

