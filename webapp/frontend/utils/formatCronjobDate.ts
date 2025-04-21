// Utility for formatting cronjob schedule to CET/CEST
export function formatCronjobDate(schedule: string): string {
  try {
    const parts = schedule.split(' ');
    if (parts.length < 5) throw new Error('Invalid cron format');
    const [min, hour, day, month] = parts;
    const utcDate = new Date(Date.UTC(
      new Date().getFullYear(),
      parseInt(month) - 1,
      parseInt(day),
      parseInt(hour),
      parseInt(min)
    ));
    const formatter = new Intl.DateTimeFormat('de-DE', {
      timeZone: 'Europe/Berlin',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
    return formatter.format(utcDate) + ' CET';
  } catch {
    return schedule;
  }
}
