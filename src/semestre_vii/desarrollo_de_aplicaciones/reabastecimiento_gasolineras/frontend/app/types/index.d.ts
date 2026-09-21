export type OrderDecision = 'accepted' | 'modified' | 'manual'
export type OrderStatus = 'pending' | 'reviewing' | 'approved'
export type StationStatus = 'ok' | 'attention'

export interface Order {
  id: string
  station: string
  product: string
  week: string
  recommendedLiters: number
  requestedLiters: number
  decision: OrderDecision
  status: OrderStatus
}

export interface Station {
  id: string
  name: string
  region: string
  manager: string
  lastClose: string
  wape: number
  status: StationStatus
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
  status: 'baseline' | 'candidate' | 'pending'
}
