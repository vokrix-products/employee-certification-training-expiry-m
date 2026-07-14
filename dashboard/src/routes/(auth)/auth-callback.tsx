import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useEffect } from 'react'
import { supabase } from '@/lib/supabase'

export const Route = createFileRoute('/(auth)/auth-callback')({
  component: AuthCallback,
})

function AuthCallback() {
  const navigate = useNavigate()
  useEffect(() => {
    // detectSessionInUrl processes #access_token automatically
    // just wait for it then navigate
    const timer = setTimeout(async () => {
      const { data } = await supabase.auth.getSession()
      if (data.session) navigate({ to: '/' })
      else navigate({ to: '/sign-up' })
    }, 1500)
    return () => clearTimeout(timer)
  }, [navigate])
  return (
    <div className='flex h-screen items-center justify-center'>
      <p className='text-muted-foreground'>Signing you in...</p>
    </div>
  )
}
