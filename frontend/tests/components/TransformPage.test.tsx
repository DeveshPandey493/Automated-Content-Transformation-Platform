import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import TransformationStudioPage from '@/app/transform/page';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
  useSearchParams: jest.fn(() => ({ get: jest.fn() })),
  useRouter: jest.fn(() => ({ push: jest.fn() })),
}));

// Mock fetch
global.fetch = jest.fn();

describe('TransformationStudioPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockReset();
  });

  it('renders transformation studio header', async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [{ id: 'doc-1', title: 'Test Doc', total_words: 100 }],
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [
          { model_id: 'extractive/textrank', name: 'TextRank', family: 'EXTRACTIVE', provider: 'LOCAL' }
        ],
      });

    render(<TransformationStudioPage />);

    await waitFor(() => {
      expect(screen.getByText('Transformation Studio')).toBeInTheDocument();
    });

    expect(screen.getByText(/Configure multi-audience synthesis/i)).toBeInTheDocument();
  });

  it('shows error when no document selected', async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

    render(<TransformationStudioPage />);

    await waitFor(() => {
      expect(screen.getByText(/No documents available/i)).toBeInTheDocument();
    });
  });

  it('allows format type selection', async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [{ id: 'doc-1', title: 'Test Doc', total_words: 100 }],
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [
          { model_id: 'extractive/textrank', name: 'TextRank', family: 'EXTRACTIVE', provider: 'LOCAL' }
        ],
      });

    render(<TransformationStudioPage />);

    await waitFor(() => {
      expect(screen.getByText('Executive Summary')).toBeInTheDocument();
    });

    // Click on Public Advisory
    fireEvent.click(screen.getByText('Public Advisory'));

    await waitFor(() => {
      // Check that format type changed - the button should show selected state
      const button = screen.getByText('Public Advisory').closest('button');
      expect(button).toHaveClass('bg-sky-500/10');
    });
  });

  it('allows audience and tone selection', async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [{ id: 'doc-1', title: 'Test Doc', total_words: 100 }],
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [
          { model_id: 'extractive/textrank', name: 'TextRank', family: 'EXTRACTIVE', provider: 'LOCAL' }
        ],
      });

    render(<TransformationStudioPage />);

    await waitFor(() => {
      expect(screen.getAllByText(/Target Audience/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Tone Calibration/i).length).toBeGreaterThan(0);
    });

    // Check that select elements exist
    const audienceSelect = screen.getByDisplayValue('Senior Management & Leadership');
    expect(audienceSelect).toBeInTheDocument();
  });

  it('allows length target selection', async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [{ id: 'doc-1', title: 'Test Doc', total_words: 100 }],
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [
          { model_id: 'extractive/textrank', name: 'TextRank', family: 'EXTRACTIVE', provider: 'LOCAL' }
        ],
      });

    render(<TransformationStudioPage />);

    await waitFor(() => {
      expect(screen.getByText('Short (~120w)')).toBeInTheDocument();
      expect(screen.getByText('Medium (~250w)')).toBeInTheDocument();
      expect(screen.getByText('Detailed (~500w)')).toBeInTheDocument();
      expect(screen.getByText('Custom Word Limit')).toBeInTheDocument();
    });

    // Click on Detailed
    fireEvent.click(screen.getByText('Detailed (~500w)'));

    await waitFor(() => {
      const button = screen.getByText('Detailed (~500w)').closest('button');
      expect(button).toHaveClass('bg-sky-500/10');
    });
  });

  it('shows generate button with correct model count', async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [{ id: 'doc-1', title: 'Test Doc', total_words: 100 }],
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [
          { model_id: 'extractive/textrank', name: 'TextRank', family: 'EXTRACTIVE', provider: 'LOCAL' },
          { model_id: 'extractive/tfidf', name: 'TFIDF', family: 'EXTRACTIVE', provider: 'LOCAL' },
        ],
      });

    render(<TransformationStudioPage />);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Execute Transformation \(1 Model\)/i })).toBeInTheDocument();
    });
  });
});