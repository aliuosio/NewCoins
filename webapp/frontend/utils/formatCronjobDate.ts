// Utility for formatting cronjob schedule to CET/CEST
export function formatCronjobDate(schedule: string): string {
  try {
    const parts = schedule.split(' ');
    if (parts.length < 5) throw new Error('Invalid cron format');
    const [min, hour, day, month] = parts;
    // Construct date assuming components are in the local timezone intended (Europe/Berlin)
    const localDate = new Date(
      new Date().getFullYear(),
      parseInt(month) - 1, // Month is 0-indexed
      parseInt(day),
      parseInt(hour),
      parseInt(min)
    );
    // Format the date explicitly for Europe/Berlin timezone display
    const formatter = new Intl.DateTimeFormat('de-DE', {
      timeZone: 'Europe/Berlin', // Ensure output matches the intended timezone
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
    // Append timezone indicator for clarity, adjust if needed (CET/CEST)
    // Note: Intl.DateTimeFormat handles DST automatically based on the date and timezone.
    // Manually appending 'CET' might be inaccurate during CEST. Consider removing or using timeZoneName.
    return formatter.format(localDate); // Removed manual ' CET' suffix
  } catch {
    return schedule; // Return original schedule on error
  }
}
