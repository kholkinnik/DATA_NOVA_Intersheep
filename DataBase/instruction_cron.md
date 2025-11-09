## Работа с CRON

# установи расширение CRON для Postgres
CREATE EXTENSION IF NOT EXISTS pg_cron;

# запусти задачи по расписанию
SELECT cron.schedule(
  'export_users_audit_daily', - название задачи
  '30 16 * * *',              - расписание запуска
  'SELECT export_today_users_audit();' - команда для запуска
);

# проверь активность задачи (запомни jobid)
SELECT * FROM cron.job;

# просмотреть детаи запуска задач
SELECT * FROM cron.job_run_details ORDER BY start_time DESC LIMIT 5;

# остановить(удалить) job из cron
SELECT cron.unschedule(jobid);

