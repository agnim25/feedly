'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { isAuthenticated, removeAuthToken } from '@/lib/auth'
import Link from 'next/link'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login')
    }
  }, [router])

  const handleLogout = () => {
    removeAuthToken()
    router.push('/login')
  }

  return (
    <div>
      <div className="bg-white border-b border-gray-200 px-6 py-3 flex justify-between items-center">
        <Link href="/dashboard" className="text-xl font-bold text-gray-900">
          Feedly
        </Link>
        <button
          onClick={handleLogout}
          className="text-sm text-gray-600 hover:text-gray-900"
        >
          Logout
        </button>
      </div>
      {children}
    </div>
  )
}
