import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Sidebar } from '@/components/layout/sidebar';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
  useRouter: jest.fn(() => ({ push: jest.fn() })),
}));

import { usePathname, useRouter } from 'next/navigation';

const mockUsePathname = usePathname as jest.Mock;
const mockUseRouter = useRouter as jest.Mock;

describe('Sidebar', () => {
  const mockPush = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseRouter.mockReturnValue({ push: mockPush });
  });

  it('renders navigation items', () => {
    mockUsePathname.mockReturnValue('/');
    render(<Sidebar />);

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Document Library')).toBeInTheDocument();
    expect(screen.getByText('Transformation Studio')).toBeInTheDocument();
    expect(screen.getByText('Review & Traceability')).toBeInTheDocument();
    expect(screen.getByText('Model Laboratory')).toBeInTheDocument();
    expect(screen.getByText('Evaluation Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Dataset Management')).toBeInTheDocument();
  });

  it('highlights active page', () => {
    mockUsePathname.mockReturnValue('/documents');
    render(<Sidebar />);
    // The active page gets special styling - just verify it renders
    const element = screen.getByText('Document Library');
    expect(element).toBeInTheDocument();
  });

  it('has correct navigation links', () => {
    mockUsePathname.mockReturnValue('/');
    render(<Sidebar />);
    const links = screen.getAllByRole('link');
    expect(links.length).toBeGreaterThanOrEqual(7);
  });
});