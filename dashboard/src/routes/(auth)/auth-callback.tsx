import { createFileRoute, redirect } from '@tanstack/react-router'
import { supabase } from '@/lib/supabase'

export const Route = createFileRoute('/(auth)/auth-callback')({
  beforeLoad: async () => {
    await supabase.auth.getSession()
    throw redirect({ to: '/' })
  },
  component: () => null,
})
