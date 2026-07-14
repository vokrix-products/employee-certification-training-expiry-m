import {
  HelpCircle,
  CircleX,
  Clock,
  CircleCheck,
  CircleAlert,
} from 'lucide-react'

export const labels = [
  { value: 'bug', label: 'Bug' },
  { value: 'feature', label: 'Feature' },
  { value: 'documentation', label: 'Documentation' },
]

export type Severity = 'critical' | 'warning' | 'good' | 'neutral'

export const severityToBadgeVariant: Record<
  Severity,
  'destructive' | 'warning' | 'success' | 'secondary'
> = {
  critical: 'destructive',
  warning: 'warning',
  good: 'success',
  neutral: 'secondary',
}

// __STATUSES_BLOCK_START__
export const statuses: {
  label: string
  value: string
  icon: typeof HelpCircle
  severity: Severity
}[] = [
  { label: 'Expired', value: 'expired', icon: CircleX, severity: 'critical' as Severity },
  { label: 'Expiring Soon', value: 'expiring_soon', icon: Clock, severity: 'warning' as Severity },
  { label: 'Valid', value: 'valid', icon: CircleCheck, severity: 'good' as Severity },
  { label: 'Missing', value: 'missing', icon: CircleAlert, severity: 'critical' as Severity },
]
// __STATUSES_BLOCK_END__
