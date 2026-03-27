# Technical Patterns — Data Visualization Implementation

Code patterns and implementation recipes for D3+React, scrollytelling, animation, maps, fal.ai, WebGL, accessibility, and Next.js integration.

---

## 1. D3 + React Core Pattern

"D3 for math, React for DOM." D3 calculates positions, scales, and paths. React renders SVG.

### Responsive Line Chart

```tsx
'use client'

import { useRef, useMemo } from 'react'
import * as d3 from 'd3'
import { useResizeObserver } from '@/lib/hooks/use-resize-observer'

interface DataPoint {
  date: Date
  value: number
}

interface LineChartProps {
  data: DataPoint[]
  title: string
  subtitle: string // The insight — always required
}

export function LineChart({ data, title, subtitle }: LineChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const { width } = useResizeObserver(containerRef)

  const margin = { top: 40, right: 20, bottom: 30, left: 50 }
  const height = Math.min(width * 0.6, 500) // Responsive aspect ratio
  const innerW = width - margin.left - margin.right
  const innerH = height - margin.top - margin.bottom

  const { xScale, yScale, linePath } = useMemo(() => {
    const x = d3.scaleTime()
      .domain(d3.extent(data, d => d.date) as [Date, Date])
      .range([0, innerW])

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value)! * 1.1])
      .range([innerH, 0])
      .nice()

    const line = d3.line<DataPoint>()
      .x(d => x(d.date))
      .y(d => y(d.value))
      .curve(d3.curveMonotoneX)

    return { xScale: x, yScale: y, linePath: line(data) }
  }, [data, innerW, innerH])

  const yTicks = yScale.ticks(5)
  const xTicks = xScale.ticks(width > 600 ? 8 : 4)

  return (
    <div ref={containerRef} className="w-full">
      <svg
        width={width}
        height={height}
        role="img"
        aria-label={subtitle}
      >
        <title>{title}</title>
        <desc>{subtitle}</desc>

        <g transform={`translate(${margin.left},${margin.top})`}>
          {/* Grid lines */}
          {yTicks.map(tick => (
            <line
              key={tick}
              x1={0} x2={innerW}
              y1={yScale(tick)} y2={yScale(tick)}
              stroke="#e5e7eb" strokeDasharray="2,2"
            />
          ))}

          {/* Y axis labels */}
          {yTicks.map(tick => (
            <text
              key={tick}
              x={-8} y={yScale(tick)}
              textAnchor="end" dominantBaseline="middle"
              className="fill-gray-500 text-xs"
            >
              {d3.format('.2s')(tick)}
            </text>
          ))}

          {/* X axis labels */}
          {xTicks.map(tick => (
            <text
              key={tick.getTime()}
              x={xScale(tick)} y={innerH + 20}
              textAnchor="middle"
              className="fill-gray-500 text-xs"
            >
              {d3.timeFormat('%b %Y')(tick)}
            </text>
          ))}

          {/* Data line */}
          <path
            d={linePath ?? ''}
            fill="none"
            stroke="var(--color-primary, #2563eb)"
            strokeWidth={2}
          />
        </g>
      </svg>
    </div>
  )
}
```

### Data Processing Patterns

```ts
import * as d3 from 'd3'

// Parse CSV with types
const data = d3.csvParse(raw, d => ({
  date: new Date(d.date),
  value: +d.value,
  category: d.category,
}))

// Rollup: aggregate by category
const byCategory = d3.rollup(data, v => d3.sum(v, d => d.value), d => d.category)

// Group: organize for small multiples
const grouped = d3.group(data, d => d.category)

// Bin: create histogram buckets
const bins = d3.bin<DataPoint, number>()
  .value(d => d.value)
  .thresholds(20)(data)

// Stack: prepare for stacked charts
const stack = d3.stack<any>()
  .keys(['series1', 'series2', 'series3'])
  .order(d3.stackOrderDescending)
```

### Scales Quick Reference

```ts
// Continuous → continuous
d3.scaleLinear().domain([0, 100]).range([0, width])
d3.scaleTime().domain([startDate, endDate]).range([0, width])
d3.scaleSqrt().domain([0, max]).range([0, 30]) // Area-proportional sizing
d3.scaleLog().domain([1, 1000]).range([0, width])

// Continuous → color
d3.scaleSequential(d3.interpolateBlues).domain([0, max])
d3.scaleDiverging(d3.interpolateRdBu).domain([min, 0, max])

// Discrete → discrete
d3.scaleBand().domain(categories).range([0, width]).padding(0.2)
d3.scaleOrdinal(d3.schemeTableau10).domain(categories)
d3.scalePoint().domain(categories).range([0, width])
```

---

## 2. Responsive Chart Hook

```tsx
'use client'

import { useEffect, useRef, useState } from 'react'

export function useResizeObserver(ref: React.RefObject<HTMLElement | null>) {
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 })

  useEffect(() => {
    const el = ref.current
    if (!el) return

    const observer = new ResizeObserver(entries => {
      const { width, height } = entries[0].contentRect
      setDimensions({ width, height })
    })

    observer.observe(el)
    return () => observer.disconnect()
  }, [ref])

  return dimensions
}

// Breakpoint-aware margins
export function useChartMargins(width: number) {
  if (width < 480) return { top: 24, right: 12, bottom: 24, left: 36 }
  if (width < 768) return { top: 32, right: 16, bottom: 28, left: 44 }
  return { top: 40, right: 20, bottom: 30, left: 50 }
}

// Aspect ratio switching: wider on desktop, taller on mobile
export function useChartHeight(width: number) {
  if (width < 480) return width * 1.2   // 5:6 portrait
  if (width < 768) return width * 0.75  // 4:3
  return Math.min(width * 0.56, 600)    // 16:9, capped
}
```

---

## 3. Scrollytelling Setup

### ScrollySection Component

```tsx
'use client'

import { useState, useRef, useEffect } from 'react'
import scrollama from 'scrollama'

interface ScrollySectionProps {
  steps: { id: string; content: React.ReactNode }[]
  chart: (activeStep: number) => React.ReactNode
}

export function ScrollySection({ steps, chart }: ScrollySectionProps) {
  const [activeStep, setActiveStep] = useState(0)
  const scrollerRef = useRef<ReturnType<typeof scrollama> | null>(null)

  useEffect(() => {
    const scroller = scrollama()

    scroller
      .setup({
        step: '[data-scrolly-step]',
        offset: 0.5,      // Trigger at middle of viewport
        progress: false,
      })
      .onStepEnter(({ index }) => setActiveStep(index))

    scrollerRef.current = scroller

    return () => scroller.destroy()
  }, [])

  return (
    <section className="relative">
      {/* Sticky chart container */}
      <div className="sticky top-0 h-screen flex items-center justify-center z-0">
        {chart(activeStep)}
      </div>

      {/* Scrollable text steps */}
      <div className="relative z-10">
        {steps.map((step, i) => (
          <div
            key={step.id}
            data-scrolly-step
            className={`
              min-h-[80vh] flex items-center px-4
              max-w-md mx-auto
              transition-opacity duration-300
              ${activeStep === i ? 'opacity-100' : 'opacity-30'}
            `}
          >
            <div className="bg-white/90 dark:bg-gray-900/90 backdrop-blur p-6 rounded-lg shadow-lg">
              {step.content}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
```

### Complete 3-Step Example

```tsx
'use client'

import { ScrollySection } from '@/components/scrolly-section'
import { LineChart } from '@/components/line-chart'

const allData = [/* ... */]

export function FundingStory() {
  return (
    <ScrollySection
      steps={[
        {
          id: 'context',
          content: (
            <p>Startup funding grew steadily from 2015 to 2021, reaching historic highs.</p>
          ),
        },
        {
          id: 'reveal',
          content: (
            <p><strong>Then it dropped 40% in a single year</strong> — the steepest decline since the dot-com bust.</p>
          ),
        },
        {
          id: 'implication',
          content: (
            <p>Early-stage rounds were hit hardest. Seed rounds fell 52%, while growth rounds held relatively steady.</p>
          ),
        },
      ]}
      chart={(step) => {
        // Step 0: show the full line, muted
        // Step 1: highlight the 2022-2023 decline with annotation
        // Step 2: split into stage-specific lines
        return <LineChart data={allData} activeStep={step} />
      }}
    />
  )
}
```

---

## 4. Animation Patterns

### Motion (framer-motion successor) for React

```tsx
'use client'

import { motion, useReducedMotion } from 'motion/react'

// Bar chart with entrance animation
function AnimatedBar({ x, y, width, height, delay }: BarProps) {
  const shouldReduce = useReducedMotion()

  return (
    <motion.rect
      x={x}
      y={y + height} // Start from bottom
      width={width}
      height={0}
      animate={{ y, height }}
      transition={shouldReduce
        ? { duration: 0 }
        : { duration: 0.5, delay, ease: 'easeOut' }
      }
      fill="var(--color-primary)"
    />
  )
}

// Line chart path drawing
function AnimatedLine({ d }: { d: string }) {
  const shouldReduce = useReducedMotion()

  return (
    <motion.path
      d={d}
      fill="none"
      stroke="var(--color-primary)"
      strokeWidth={2}
      initial={shouldReduce ? {} : { pathLength: 0 }}
      animate={{ pathLength: 1 }}
      transition={shouldReduce
        ? { duration: 0 }
        : { duration: 1.5, ease: 'easeInOut' }
      }
    />
  )
}

// Spring transition between data states
function DataPoint({ cx, cy }: { cx: number; cy: number }) {
  return (
    <motion.circle
      cx={cx}
      cy={cy}
      r={4}
      fill="var(--color-primary)"
      layout // Smooth transition when cx/cy change
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
    />
  )
}
```

### prefers-reduced-motion Hook

```tsx
import { useEffect, useState } from 'react'

export function usePrefersReducedMotion() {
  const [reduces, setReduces] = useState(false)

  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReduces(mq.matches)

    const handler = (e: MediaQueryListEvent) => setReduces(e.matches)
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [])

  return reduces
}
```

---

## 5. Map Patterns

### D3-Geo Static Choropleth

```tsx
'use client'

import { useMemo } from 'react'
import * as d3 from 'd3'
import * as topojson from 'topojson-client'
import type { Topology } from 'topojson-specification'

interface ChoroplethProps {
  topology: Topology
  data: Map<string, number>
  title: string
  subtitle: string
}

export function Choropleth({ topology, data, title, subtitle }: ChoroplethProps) {
  const features = topojson.feature(topology, topology.objects.states)
  const mesh = topojson.mesh(topology, topology.objects.states, (a, b) => a !== b)

  const color = useMemo(() => {
    const values = Array.from(data.values())
    return d3.scaleSequential(d3.interpolateBlues)
      .domain([d3.min(values)!, d3.max(values)!])
  }, [data])

  const projection = d3.geoAlbersUsa().fitSize([960, 600], features)
  const path = d3.geoPath(projection)

  return (
    <svg viewBox="0 0 960 600" role="img" aria-label={subtitle}>
      <title>{title}</title>
      {'features' in features && features.features.map((f: any) => (
        <path
          key={f.id}
          d={path(f) ?? ''}
          fill={data.has(f.id) ? color(data.get(f.id)!) : '#eee'}
          stroke="#fff"
          strokeWidth={0.5}
        />
      ))}
      <path d={path(mesh) ?? ''} fill="none" stroke="#999" strokeWidth={0.5} />
    </svg>
  )
}
```

### MapLibre Interactive Map

```tsx
'use client'

import { useEffect, useRef } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

export function InteractiveMap({ data }: { data: GeoJSON.FeatureCollection }) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
      center: [-98, 39],
      zoom: 4,
    })

    map.on('load', () => {
      map.addSource('data', { type: 'geojson', data })
      map.addLayer({
        id: 'points',
        type: 'circle',
        source: 'data',
        paint: {
          'circle-radius': ['interpolate', ['linear'], ['get', 'value'], 0, 3, 100, 20],
          'circle-color': '#3b82f6',
          'circle-opacity': 0.7,
        },
      })
    })

    return () => map.remove()
  }, [data])

  return <div ref={containerRef} className="w-full h-[500px] rounded-lg" />
}
```

### TopoJSON Optimization

```bash
# Convert GeoJSON to TopoJSON (80-95% smaller)
# Install: bun add -g topojson-server topojson-client topojson-simplify
geo2topo states=states.geojson > states.topo.json
toposimplify -p 0.01 states.topo.json > states-simplified.topo.json
topoquantize 1e5 states-simplified.topo.json > states-final.topo.json
```

---

## 6. fal.ai Integration

For editorial illustrations and backgrounds — never for the charts themselves.

### Setup

```bash
bun add @fal-ai/client
```

### Editorial Illustration Generation

```ts
import { fal } from '@fal-ai/client'

fal.config({ credentials: process.env.FAL_API_KEY })

// Generate editorial illustration for a data story
async function generateEditorialImage(concept: string) {
  const result = await fal.subscribe('fal-ai/flux/schnell', {
    input: {
      prompt: `Editorial illustration for data journalism article about ${concept}.
        Clean, minimalist style. Muted color palette with one accent color.
        No text, no charts, no graphs. Abstract conceptual illustration.`,
      image_size: 'landscape_16_9',
      num_images: 1,
    },
  })

  return result.data.images[0].url
}
```

### Next.js API Route with Caching

```ts
// app/api/illustration/route.ts
import { fal } from '@fal-ai/client'
import { NextRequest, NextResponse } from 'next/server'

fal.config({ credentials: process.env.FAL_API_KEY })

export async function POST(req: NextRequest) {
  const { concept, style = 'editorial' } = await req.json()

  const result = await fal.subscribe('fal-ai/flux/schnell', {
    input: {
      prompt: `${style} illustration: ${concept}. Minimalist, data journalism aesthetic.`,
      image_size: 'landscape_16_9',
      num_images: 1,
    },
  })

  return NextResponse.json(
    { url: result.data.images[0].url },
    {
      headers: {
        'Cache-Control': 'public, max-age=86400, s-maxage=604800',
      },
    }
  )
}
```

---

## 7. WebGL Patterns

### deck.gl ScatterplotLayer

```tsx
'use client'

import { DeckGL } from '@deck.gl/react'
import { ScatterplotLayer } from '@deck.gl/layers'
import { Map } from 'react-map-gl/maplibre'

interface Point {
  position: [number, number]
  value: number
  category: string
}

export function LargeScatterMap({ data }: { data: Point[] }) {
  const layers = [
    new ScatterplotLayer<Point>({
      id: 'scatter',
      data,
      getPosition: d => d.position,
      getRadius: d => Math.sqrt(d.value) * 100,
      getFillColor: d => {
        const colors: Record<string, [number, number, number, number]> = {
          tech: [59, 130, 246, 180],
          health: [16, 185, 129, 180],
          finance: [245, 158, 11, 180],
        }
        return colors[d.category] ?? [156, 163, 175, 180]
      },
      pickable: true,
      radiusMinPixels: 2,
      radiusMaxPixels: 40,
    }),
  ]

  return (
    <DeckGL
      initialViewState={{ longitude: -98, latitude: 39, zoom: 4 }}
      controller
      layers={layers}
    >
      <Map mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json" />
    </DeckGL>
  )
}
```

### Canvas Fallback with Quadtree Hit Detection

```tsx
'use client'

import { useRef, useEffect, useCallback } from 'react'
import * as d3 from 'd3'

export function CanvasScatter({ data, width, height }: CanvasScatterProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const quadtree = d3.quadtree<DataPoint>()
    .x(d => xScale(d.x))
    .y(d => yScale(d.y))
    .addAll(data)

  // Efficient hit detection for tooltips
  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    const rect = canvasRef.current!.getBoundingClientRect()
    const mx = e.clientX - rect.left
    const my = e.clientY - rect.top
    const closest = quadtree.find(mx, my, 20) // 20px search radius
    // Show tooltip for `closest`
  }, [quadtree])

  useEffect(() => {
    const ctx = canvasRef.current?.getContext('2d')
    if (!ctx) return

    ctx.clearRect(0, 0, width, height)
    data.forEach(d => {
      ctx.beginPath()
      ctx.arc(xScale(d.x), yScale(d.y), 3, 0, 2 * Math.PI)
      ctx.fillStyle = 'rgba(59, 130, 246, 0.5)'
      ctx.fill()
    })
  }, [data, width, height])

  return <canvas ref={canvasRef} width={width} height={height} onMouseMove={handleMouseMove} />
}
```

### Performance Rules

- **< 1,000 elements**: SVG (accessible, inspectable, crisp at all sizes)
- **1,000–50,000**: Canvas 2D (fast draw, custom hit detection via quadtree)
- **50,000+**: WebGL via deck.gl (GPU-accelerated, handles millions)
- Always provide a Canvas fallback for WebGL (some devices lack support)
- Use `requestAnimationFrame` for Canvas animations, never `setInterval`
- Debounce resize handlers (150ms) to prevent layout thrash

---

## 8. Accessible SVG Structure

### Complete Accessible Chart Template

```tsx
<svg
  role="img"
  aria-label="Line chart showing startup funding dropped 40% in 2023"
  aria-describedby="chart-desc"
>
  <title>Startup Funding by Year</title>
  <desc id="chart-desc">
    Annual startup funding from 2015 to 2024. Funding peaked at $330B in 2021
    before declining to $200B in 2023, a 40% drop and the steepest decline
    since the dot-com bust.
  </desc>

  {/* Chart content */}
  <g role="list" aria-label="Data points">
    {data.map((d, i) => (
      <circle
        key={i}
        role="listitem"
        aria-label={`${d3.timeFormat('%B %Y')(d.date)}: $${d.value}B`}
        tabIndex={0}
        cx={xScale(d.date)}
        cy={yScale(d.value)}
        r={4}
      />
    ))}
  </g>
</svg>

{/* Hidden data table for screen readers */}
<table className="sr-only">
  <caption>Startup Funding by Year</caption>
  <thead>
    <tr><th>Year</th><th>Funding ($B)</th></tr>
  </thead>
  <tbody>
    {data.map(d => (
      <tr key={d.date.getTime()}>
        <td>{d3.timeFormat('%Y')(d.date)}</td>
        <td>{d.value}</td>
      </tr>
    ))}
  </tbody>
</table>
```

### Interactive Accessibility

```tsx
// Arrow key navigation between data points
function useChartKeyNav(dataLength: number) {
  const [activeIndex, setActiveIndex] = useState(0)

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        e.preventDefault()
        setActiveIndex(i => Math.min(i + 1, dataLength - 1))
        break
      case 'ArrowLeft':
      case 'ArrowUp':
        e.preventDefault()
        setActiveIndex(i => Math.max(i - 1, 0))
        break
      case 'Home':
        e.preventDefault()
        setActiveIndex(0)
        break
      case 'End':
        e.preventDefault()
        setActiveIndex(dataLength - 1)
        break
    }
  }, [dataLength])

  return { activeIndex, handleKeyDown }
}
```

---

## 9. Next.js Integration

### Client Components for Visualization

```tsx
// components/charts/funding-chart.tsx
'use client' // Required — D3 + event handlers need the browser

import { LineChart } from './line-chart'

export function FundingChart({ data }: { data: DataPoint[] }) {
  return <LineChart data={data} title="..." subtitle="..." />
}
```

### Server-Side Data Fetching

```tsx
// app/dashboard/page.tsx (Server Component)
import { FundingChart } from '@/components/charts/funding-chart'
import { getFundingData } from '@/lib/data'

export default async function DashboardPage() {
  const data = await getFundingData() // Runs on server

  return (
    <main>
      <h1>Funding Dashboard</h1>
      <FundingChart data={data} /> {/* Client component */}
    </main>
  )
}
```

### Bundle Optimization

```ts
// next.config.ts — tree-shake D3 by importing specific modules
// DON'T: import * as d3 from 'd3'           (~500KB)
// DO:    import { scaleLinear } from 'd3-scale' (~30KB)

// For large viz pages, use dynamic imports
import dynamic from 'next/dynamic'

const HeavyMap = dynamic(() => import('@/components/charts/heavy-map'), {
  ssr: false, // Maps need browser APIs
  loading: () => <div className="h-[500px] animate-pulse bg-muted rounded-lg" />,
})
```

### Lazy Loading Below-Fold Charts

```tsx
'use client'

import { useInView } from 'react-intersection-observer'
import dynamic from 'next/dynamic'

const Chart = dynamic(() => import('./expensive-chart'), { ssr: false })

export function LazyChart(props: ChartProps) {
  const { ref, inView } = useInView({ triggerOnce: true, rootMargin: '200px' })

  return (
    <div ref={ref} className="min-h-[400px]">
      {inView ? <Chart {...props} /> : <div className="animate-pulse bg-muted h-[400px] rounded-lg" />}
    </div>
  )
}
```
