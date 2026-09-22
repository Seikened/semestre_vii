import type { ForecastPoint, FuelOrder, FuelStation, ModelCandidate } from '~/types'

export const fuelOrders: FuelOrder[] = [
  { id: 'PED-1048', station: 'León Centro 01', stationId: 'GAS-001', week: '2026-W39', product: 'Regular', recommendedLiters: 21800, requestedLiters: 22000, decision: 'accepted', status: 'pending', createdAt: '2026-09-21T16:18:00-06:00', note: 'Cierre semanal completo. La sucursal mantuvo la recomendación casi sin cambios.' },
  { id: 'PED-1047', station: 'Silao Norte 03', stationId: 'GAS-003', week: '2026-W39', product: 'Diésel', recommendedLiters: 16400, requestedLiters: 18000, decision: 'modified', status: 'reviewing', createdAt: '2026-09-21T15:42:00-06:00', note: 'La sucursal aumentó el pedido por una entrega programada y mayor demanda esperada.' },
  { id: 'PED-1046', station: 'Irapuato Sur 02', stationId: 'GAS-012', week: '2026-W39', product: 'Premium', recommendedLiters: 9400, requestedLiters: 9000, decision: 'modified', status: 'pending', createdAt: '2026-09-21T14:35:00-06:00', note: 'Ajuste manual menor respecto a la sugerencia.' },
  { id: 'PED-1045', station: 'Celaya Oriente 05', stationId: 'GAS-021', week: '2026-W39', product: 'Regular', recommendedLiters: 24100, requestedLiters: 24000, decision: 'accepted', status: 'approved', createdAt: '2026-09-21T13:08:00-06:00', note: 'Pedido revisado y aprobado en la maqueta.' },
  { id: 'PED-1044', station: 'Salamanca Centro 04', stationId: 'GAS-029', week: '2026-W39', product: 'Diésel', recommendedLiters: 13100, requestedLiters: 15000, decision: 'manual', status: 'reviewing', createdAt: '2026-09-21T12:17:00-06:00', note: 'Captura manual. Requiere revisión por diferencia contra la recomendación.' },
  { id: 'PED-1043', station: 'León Norte 07', stationId: 'GAS-038', week: '2026-W39', product: 'Premium', recommendedLiters: 11200, requestedLiters: 11200, decision: 'accepted', status: 'approved', createdAt: '2026-09-21T11:54:00-06:00', note: 'Recomendación aceptada sin cambios.' },
  { id: 'PED-1042', station: 'Guanajuato 02', stationId: 'GAS-044', week: '2026-W39', product: 'Regular', recommendedLiters: 19600, requestedLiters: 20000, decision: 'modified', status: 'pending', createdAt: '2026-09-21T10:22:00-06:00', note: 'Ajuste manual moderado.' },
  { id: 'PED-1041', station: 'San Francisco 06', stationId: 'GAS-052', week: '2026-W39', product: 'Regular', recommendedLiters: 17300, requestedLiters: 17500, decision: 'accepted', status: 'pending', createdAt: '2026-09-21T09:46:00-06:00', note: 'Pedido dentro del rango esperado.' }
]

export const fuelStations: FuelStation[] = [
  { id: 'GAS-001', name: 'León Centro 01', region: 'León', manager: 'Mariana López', lastClose: '20 sep 2026', wape: 6.8, status: 'stable' },
  { id: 'GAS-003', name: 'Silao Norte 03', region: 'Silao', manager: 'Luis Ramírez', lastClose: '20 sep 2026', wape: 11.9, status: 'attention' },
  { id: 'GAS-012', name: 'Irapuato Sur 02', region: 'Irapuato', manager: 'Andrea Torres', lastClose: '20 sep 2026', wape: 7.4, status: 'stable' },
  { id: 'GAS-021', name: 'Celaya Oriente 05', region: 'Celaya', manager: 'Jorge Ruiz', lastClose: '20 sep 2026', wape: 8.1, status: 'stable' },
  { id: 'GAS-029', name: 'Salamanca Centro 04', region: 'Salamanca', manager: 'Diana Soto', lastClose: '19 sep 2026', wape: 13.2, status: 'attention' },
  { id: 'GAS-038', name: 'León Norte 07', region: 'León', manager: 'Mónica Vega', lastClose: '20 sep 2026', wape: 5.9, status: 'stable' },
  { id: 'GAS-044', name: 'Guanajuato 02', region: 'Guanajuato', manager: 'Carlos Méndez', lastClose: '20 sep 2026', wape: 9.0, status: 'stable' },
  { id: 'GAS-052', name: 'San Francisco 06', region: 'San Francisco', manager: 'Paola Silva', lastClose: '20 sep 2026', wape: 8.6, status: 'stable' },
  { id: 'GAS-061', name: 'Romita 01', region: 'Romita', manager: 'Rodrigo León', lastClose: '20 sep 2026', wape: 7.9, status: 'stable' },
  { id: 'GAS-074', name: 'Pénjamo 03', region: 'Pénjamo', manager: 'Sofía Castro', lastClose: '18 sep 2026', wape: 14.7, status: 'attention' },
  { id: 'GAS-083', name: 'Abasolo 02', region: 'Abasolo', manager: 'Ricardo Luna', lastClose: '20 sep 2026', wape: 6.5, status: 'stable' },
  { id: 'GAS-097', name: 'Acámbaro 04', region: 'Acámbaro', manager: 'Gabriela Díaz', lastClose: '19 sep 2026', wape: 10.8, status: 'attention' }
]

export const forecastPoints: ForecastPoint[] = [
  { week: 'W32', actual: 1680, forecast: 1710 },
  { week: 'W33', actual: 1760, forecast: 1740 },
  { week: 'W34', actual: 1735, forecast: 1780 },
  { week: 'W35', actual: 1840, forecast: 1810 },
  { week: 'W36', actual: 1885, forecast: 1900 },
  { week: 'W37', actual: 1940, forecast: 1915 },
  { week: 'W38', actual: 1995, forecast: 2020 },
  { week: 'W39', actual: 2050, forecast: 2080 }
]

export const modelCandidates: ModelCandidate[] = [
  { name: 'Seasonal Naive', family: 'Baseline', wape: '11.2 %', bias: '+1.7 %', status: 'baseline' },
  { name: 'Lagged GBM', family: 'Tabular', wape: '9.6 %', bias: '-0.8 %', status: 'candidate' },
  { name: 'Chronos-2', family: 'Foundation model', wape: '—', bias: '—', status: 'pending' },
  { name: 'TimesFM-3', family: 'Foundation model', wape: '—', bias: '—', status: 'pending' }
]
