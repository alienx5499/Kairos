export const SEVERITIES = {
  P1_CRITICAL: { label: 'Critical', short: 'P1' },
  P2_HIGH: { label: 'High', short: 'P2' },
  P3_MEDIUM: { label: 'Medium', short: 'P3' },
  P4_LOW: { label: 'Low', short: 'P4' }
};

export const STATUSES = {
  INVESTIGATING: 'Investigating',
  IDENTIFIED: 'Identified',
  MITIGATED: 'Mitigated',
  RESOLVED: 'Resolved'
};

const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
const UNITS = [
  ['year', 31536000],
  ['month', 2592000],
  ['day', 86400],
  ['hour', 3600],
  ['minute', 60]
];

export function relativeTime(iso) {
  if (!iso) return '';
  // backend sends naive utc timestamps
  const utc = /[zZ]|[+-]\d\d:\d\d$/.test(iso) ? iso : `${iso}Z`;
  const seconds = (new Date(utc).getTime() - Date.now()) / 1000;
  for (const [unit, size] of UNITS) {
    if (Math.abs(seconds) >= size) return rtf.format(Math.round(seconds / size), unit);
  }
  return 'just now';
}
