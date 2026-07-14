import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useEffect } from 'react'
import { supabase } from '@/lib/supabase'

export const Route = createFileRoute('/(auth)/auth-callback')({
  component: AuthCallback,
})

function AuthCallback() {
  const navigate = useNavigate()
  useEffect(() => {
    console.log('auth-callback mounted, hash:', window.location.hash.slice(0, 50))
    const timer = setTimeout(async () => {
      const { data, error } = await supabase.auth.getSession()
      console.log('session:', data.session?.user?.email, 'error:', error?.message)
      if (data.session) navigate({ to: '/' })
      else navigate({ to: '/sign-up' })
    }, 2000)
    return () => clearTimeout(timer)
  }, [navigate])
  return (
    <div className='flex h-screen items-center justify-center'>
      <p className='text-muted-foreground'>Signing you in...</p>
    </div>
  )
}
