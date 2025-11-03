import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import Login from './Login';

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

describe('Login', () => {
  test('renders login page', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    expect(screen.getByText('AI Email Sorter')).toBeInTheDocument();
    expect(screen.getByText('Sign in with Google')).toBeInTheDocument();
  });

  test('displays tagline', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    expect(screen.getByText('Organize your emails intelligently with AI')).toBeInTheDocument();
  });
});

