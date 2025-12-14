import { describe, it, expect } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import StatsCard from '../../components/dashboard/StatsCard';

describe('StatsCard Component', () => {
  // Provide a dummy icon component for tests
  const DummyIcon = () => <span data-testid="icon">*</span>;
  const defaultColor = 'text-blue';

  it('renders with title and value', () => {
    vi.useFakeTimers();
    render(
      <StatsCard
        title="Total Alerts"
        value={93}
        icon={DummyIcon}
        color={defaultColor}
        trend="+12%"
      />
    );
    act(() => {
      vi.advanceTimersByTime(800);
    });
    expect(screen.getByText('Total Alerts')).toBeInTheDocument();
    expect(screen.getByText('93')).toBeInTheDocument();
    expect(screen.getByText('+12%')).toBeInTheDocument();
    vi.useRealTimers();
  });

  it('animates value from 0 to target', () => {
    vi.useFakeTimers();
    render(
      <StatsCard
        title="New Alerts"
        value={50}
        icon={DummyIcon}
        color={defaultColor}
      />
    );
    act(() => {
      vi.advanceTimersByTime(800);
    });
    expect(screen.getByText('50')).toBeInTheDocument();
    vi.useRealTimers();
  });

  it('displays trend indicator correctly', () => {
    render(
      <StatsCard
        title="Critical Alerts"
        value={77}
        icon={DummyIcon}
        color={defaultColor}
        trend="-5%"
      />
    );

    expect(screen.getByText('-5%')).toBeInTheDocument();
  });

  it('handles zero value correctly', () => {
    render(
      <StatsCard
        title="Resolved Alerts"
        value={0}
        icon={DummyIcon}
        color={defaultColor}
      />
    );

    expect(screen.getByText('0')).toBeInTheDocument();
  });
});
