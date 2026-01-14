'use client'

import { useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { authApi } from '@/lib/api'
import { setAuthToken } from '@/lib/auth'

export default function GoogleCallbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    const code = searchParams.get('code')
    if (code) {
      handleCallback(code)
    } else {
      router.push('/login?error=no_code')
    }
  }, [searchParams, router])

  const handleCallback = async (code: string) => {
    try {
      const data = await authApi.googleCallback(code)
      setAuthToken(data.access_token)
      router.push('/dashboard')
    } catch (err: any) {
      router.push(`/login?error=${encodeURIComponent(err.response?.data?.detail || 'Authentication failed')}`)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Completing sign in...</p>
      </div>
    </div>
  )
}

