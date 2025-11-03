import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import Dashboard from './Dashboard';
import * as api from '../api';

jest.mock('../api');
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

const mockCategories = [
  { id: 1, name: 'Newsletters', description: 'Marketing emails', created_at: '2024-01-01', email_count: 5 },
  { id: 2, name: 'Receipts', description: 'Purchase receipts', created_at: '2024-01-01', email_count: 3 }
];

const mockAccounts = [
  { id: 1, email: 'test@example.com', is_primary: true, created_at: '2024-01-01', last_synced: null }
];

describe('Dashboard', () => {
  beforeEach(() => {
    (api.categoriesAPI.list as jest.Mock).mockResolvedValue(mockCategories);
    (api.accountsAPI.list as jest.Mock).mockResolvedValue(mockAccounts);
    (api.emailsAPI.listByCategory as jest.Mock).mockResolvedValue([]);
  });

  test('renders dashboard with categories', async () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      const newsletterElements = screen.getAllByText('Newsletters');
      const receiptsElements = screen.getAllByText('Receipts');
      
      expect(newsletterElements.length).toBeGreaterThan(0);
      expect(receiptsElements.length).toBeGreaterThan(0);
    });
  });

  test('displays gmail accounts', async () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
    });
  });

  test('shows add category button', async () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('+ Add Category')).toBeInTheDocument();
    });
  });

  test('shows sync emails button', async () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Sync Emails')).toBeInTheDocument();
    });
  });
});

