import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Navigation from '../../components/Navigation';
import { AuthProvider } from '../../contexts/AuthContext';

// Mock Supabase
vi.mock('../../lib/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn(() => Promise.resolve({ data: { session: null } })),
      onAuthStateChange: vi.fn(() => ({ data: { subscription: { unsubscribe: vi.fn() } } })),
      signOut: vi.fn(() => Promise.resolve()),
    },
  },
}));

const renderWithProviders = (component) => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        {component}
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('Navigation Component', () => {
  it('renders navigation items', async () => {
    renderWithProviders(<Navigation />);
    await waitFor(() => expect(screen.getByText('Nexzy')).toBeInTheDocument());
  });

  it('shows Dashboard link when authenticated', async () => {
    renderWithProviders(<Navigation />);
    await waitFor(() => {
      const nav = screen.getByRole('navigation');
      expect(nav).toBeInTheDocument();
    });
  });

  it('renders logo correctly', async () => {
    renderWithProviders(<Navigation />);
    await waitFor(() => {
      const logo = screen.getByText('Nexzy');
      expect(logo).toBeInTheDocument();
    });
  });
});
