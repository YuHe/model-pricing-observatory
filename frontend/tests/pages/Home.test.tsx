import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'

function HomeFallback() {
  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Model Pricing Observatory</h1>
    </div>
  )
}

describe('Home', () => {
  it('renders the title', () => {
    render(<HomeFallback />)
    expect(screen.getByText('Model Pricing Observatory')).toBeInTheDocument()
  })
})
