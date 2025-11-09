--Создание таблицы users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,
    role TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
--Создание таблицы для аудита изменений данных о пользователях
CREATE TABLE users_audit (
    id SERIAL PRIMARY KEY,
    user_id INTEGER, -- id user
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- дата изменений
    changed_by TEXT, -- пользователь внесший изменения
    field_changed TEXT, -- изменненная колонка
    old_value TEXT, -- старое значение
    new_value text -- новое значение
);

--создание функции записывающей изменения из таблицы users в таблицу users_audit
CREATE OR REPLACE FUNCTION log_user_audit()
RETURNS TRIGGER 
AS $$
    BEGIN
        IF OLD.name IS DISTINCT FROM NEW.name THEN
            INSERT INTO users_audit(user_id, changed_by, field_changed, old_value, new_value )
            VALUES (OLD.id, current_user, 'name', OLD.name,  NEW.name);
        END IF;

        IF OLD.email IS DISTINCT FROM NEW.email THEN
            INSERT INTO users_audit(user_id, changed_by, field_changed, old_value, new_value )
            VALUES (OLD.id, current_user, 'email', OLD.email,  NEW.email);
        END IF;

        IF OLD.role IS DISTINCT FROM NEW.role THEN
            INSERT INTO users_audit(user_id, changed_by, field_changed, old_value, new_value )
            VALUES (OLD.id, current_user, 'role', OLD.role,  NEW.role);
        END IF;

        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;

--Создание тригерра, для срабатывания функции
CREATE TRIGGER trigger_log_user_audit
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION log_user_audit();

-- первая вставка в таблицу
INSERT INTO users (name, email, role)
VALUES 
('Ivan Ivanov', 'ivan@example.com', 'DE'),
('Anna Petrova', 'anna@example.com', 'DA');

-- Обновление данных
UPDATE users
SET name  = 'INSERT_name'
WHERE role = 'DA';



-- создание функции выгружающей данные в CSV формат за дату Т-1 -- 
CREATE OR REPLACE FUNCTION export_users_audit_daily()
RETURNS void AS $$
DECLARE
    file_path text;
BEGIN
    -- Формируем путь с текущей датой
    file_path := '/tmp/users_audit_export_' || to_char(CURRENT_DATE, 'YYYY-MM-DD') || '.csv';
    -- Выполняем экспорт в CSV с заголовком
    EXECUTE format(
        'COPY (SELECT * FROM users_audit WHERE changed_at < CURRENT_DATE AND changed_at > CURRENT_DATE - interval ''2 day'') TO %L CSV HEADER',
        file_path
    );
END;
$$ LANGUAGE plpgsql;


-- CRON--
-- запуск расширения
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- запуск задачи по расписанию
SELECT cron.schedule(
  'export_users_audit_daily', - название задачи
  '0 3 * * *',              - расписание запуска
  'SELECT export_today_users_audit();' - команда для запуска
);

-- проверить список запланированных заданий через расширение pg_cron
SELECT * FROM cron.job;

