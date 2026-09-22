import type { AvatarProps } from '@nuxt/ui'

export type UserStatus = 'subscribed' | 'unsubscribed' | 'bounced'
export type SaleStatus = 'paid' | 'failed' | 'refunded'

export interface User {
  id: number
  name: string
  email: string
  avatar?: AvatarProps
  status: UserStatus
  location: string
}

export interface Mail {
  id: number
  unread?: boolean
  from: User
  subject: string
  body: string
  date: string
}

export interface Member {
  name: string
  username: string
  role: 'member' | 'owner'
  avatar: AvatarProps
}

export interface Stat {
  title: string
  icon: string
  value: number | string
  variation: number
  formatter?: (value: number) => string
}

export interface Sale {
  id: string
  date: string
  status: SaleStatus
  email: string
  amount: number
}

export interface Notification {
  id: number
  unread?: boolean
  sender: User
  body: string
  date: string
}

export type Period = 'daily' | 'weekly' | 'monthly'

export interface Range {
  start: Date
  end: Date
}

export type FuelOrderDecision = 'accepted' | 'modified' | 'manual'
export type FuelOrderStatus = 'pending' | 'reviewing' | 'approved'

export interface FuelOrder {
  id: string
  station: string
  stationId: string
  week: string
  product: string
  recommendedLiters: number
  requestedLiters: number
  decision: FuelOrderDecision
  status: FuelOrderStatus
  createdAt: string
  note: string
}

export type FuelStationStatus = 'stable' | 'attention'

export interface FuelStation {
  id: string
  name: string
  region: string
  manager: string
  lastClose: string
  wape: number
  status: FuelStationStatus
}

export interface ForecastPoint {
  week: string
  actual: number
  forecast: number
}

export interface ModelCandidate {
  name: string
  family: string
  wape: string
  bias: string
  status: 'baseline' | 'candidate' | 'pending'
}
