import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { PriceChange } from '@/components/PriceChange'

describe('PriceChange', () => {
  it('shows green down arrow for negative', () => {
    render(<PriceChange percent={-12.5} />)
    expect(screen.getByText(/▼ 12.5%/)).toBeInTheDocument()
  })
  it('shows red up arrow for positive', () => {
    render(<PriceChange percent={8.3} />)
    expect(screen.getByText(/▲ 8.3%/)).toBeInTheDocument()
  })
  it('shows dash for null', () => {
    render(<PriceChange percent={null} />)
    expect(screen.getByText('—')).toBeInTheDocument()
  })
})
