import StatsCard from './StatsCard';

export default function DashboardStats({ stats }) {
  if (!stats) return null;
  const cards = [
    { label: 'New Alerts', value: stats.new_alerts },
    { label: 'Credentials Leaked', value: stats.credentials_leaked },
    { label: 'Critical Threats', value: stats.alerts_critical },
    { label: 'Resolved', value: stats.alerts_resolved },
  ];
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {cards.map((c) => (
        <StatsCard key={c.label} label={c.label} value={c.value} />
      ))}
    </div>
  );
}
