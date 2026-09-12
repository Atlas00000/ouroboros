# Backup & restore (W2·D4 / N9)

Local dumps use the running `ouroboros-postgres` container (`pg_dump` / `pg_restore` via Docker).

## Schedule

| Job | Script | Cadence | RPO |
| --- | --- | --- | --- |
| Full DB | `python ops/backups/backup_full.py` | Nightly | Prices <= 24h (re-backfillable from MT5) |
| Irreplaceable tables | `python ops/backups/backup_targeted.py` | Hourly | Sentiment / forecast_log / outbox / profiles / … <= 1h |

Artifacts land in `data/backups/{full,targeted}/` (gitignored).

### Windows Task Scheduler (example)

```powershell
# Nightly 02:15
schtasks /Create /TN OuroborosFullBackup /SC DAILY /ST 02:15 /TR "py -3.12 C:\path\to\Ouroboros\ops\backups\backup_full.py"

# Hourly
schtasks /Create /TN OuroborosTargetedBackup /SC HOURLY /TR "py -3.12 C:\path\to\Ouroboros\ops\backups\backup_targeted.py"
```

### Linux cron (Railway jump host / VM)

```cron
15 2 * * * cd /opt/ouroboros && python ops/backups/backup_full.py
5 * * * *  cd /opt/ouroboros && python ops/backups/backup_targeted.py
```

## Restore drill

```powershell
py -3.12 ops\backups\backup_full.py
py -3.12 ops\backups\restore_drill.py
# optional: keep scratch DB
py -3.12 ops\backups\restore_drill.py --keep
```

See [docs/runbooks/restore-from-backup.md](../../docs/runbooks/restore-from-backup.md).
