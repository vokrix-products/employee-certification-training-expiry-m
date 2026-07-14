import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useEffect } from 'react'
import { supabase } from '@/lib/supabase'

export const Route = createFileRoute('/(auth)/auth-callback')({
  component: AuthCallback,
})

function AuthCallback() {
  const navigate = useNavigate()
  useEffect(() => {
    const code = new URLSearchParams(window.location.search).get('code')
    if (code) {
      supabase.auth.exchangeCodeForSession(code).then(() => {
        navigate({ to: '/' })
      })
    } else {
      supabase.auth.getSession().then(({ data: { session } }) => {
        if (session) navigate({ to: '/' })
        else navigate({ to: '/sign-up' })
      })
    }
  }, [navigate])
  return (
    <div className='flex h-screen items-center justify-center'>
      <p className='text-muted-foreground'>Signing you in...</p>
    </div>
  )
}
