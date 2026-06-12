import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { StatsCard } from '@/components/StatsCard'

describe('StatsCard', () => {
  it('renders label and value', () => {
    render(<StatsCard label="Models" value={156} />)
    expect(screen.getByText('Models')).toBeInTheDocument()
    expect(screen.getByText('156')).toBeInTheDocument()
  })
})
