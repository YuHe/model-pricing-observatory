import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { Navbar } from '@/components/Navbar'

describe('Navbar', () => {
  it('renders all nav links', () => {
    render(<Navbar />)
    expect(screen.getByText('Models')).toBeInTheDocument()
    expect(screen.getByText('Compare')).toBeInTheDocument()
    expect(screen.getByText('Providers')).toBeInTheDocument()
    expect(screen.getByText('Plans')).toBeInTheDocument()
    expect(screen.getByText('Admin')).toBeInTheDocument()
  })
})
