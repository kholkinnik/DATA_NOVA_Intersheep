--ТРИГЕРЫ - это запрос который автоматически выполняется во время выполнения операций INSERT, UPDATE, DELETE-- 
-- привязывается к таблице и если она будет удалена то и тригер тоже-- 
-- в Postgres нельзя создавать тригер с выполнением действий, к нему необходимо привязать выполнение функции
DROP TABLE IF EXISTS test.Users;
CREATE TABLE test.Users
(
    id           SERIAL,
    name         VARCHAR(20),
    surname      VARCHAR(20),
    phone_number VARCHAR(20),
    PRIMARY KEY (id)
);

INSERT INTO test.Users (name, surname, phone_number)
VALUES ('Matt', 'Damon', '+79087333025'),
       ('Edward', 'Norton', '+79642218964'),
       ('Nicolas', 'Cage', '+79808814813'),
       ('Ben', 'Affleck', '+79042778299'),
       ('John', 'Travolta', '+79640950623');
-- создание тригера при котором при вводе нового пользователя телефон всегда переводится в новый формат--
-- +7dddddddddd
-- созданием тригерной функции -- 
create or replace function modify_mobile()
returns trigger as 
$$
	begin 
		new.phone_number := CONCAT('+7',right(REPLACE(new.phone_number, ' ',''),10));
		return new;
	end;
$$ language plpgsql;


create trigger modifie_mobile
	before insert
	on test.users
	for each row
	execute function modify_mobile();

-- тест -- 
select CONCAT('+7',right(REPLACE('+7 964 593 38 19', ' ',''),10));
INSERT INTO test.Users (name, surname, phone_number)
VALUES ('Matt', 'Damon', '+8 964 593 38 19');

-- создание таблиц --
DROP TABLE IF EXISTS test.User_1EmailHistory;
DROP TABLE IF EXISTS Users_1;

-- Создание таблицы Users
CREATE TABLE test.Users_1
(
    id      serial,
    name    VARCHAR(20),
    surname VARCHAR(20),
    email   VARCHAR(40),
    PRIMARY KEY (id)
);

INSERT INTO test.Users_1 (name, surname, email)
VALUES ('Matt', 'Damon', 'matt@gmail.com'),
       ('Edward', 'Norton', 'ENorton.@outlook.com'),
       ('Nicolas', 'Cage', 'ghostrider@outlook.com'),
       ('Ben', 'Affleck', 'thebestbat@gmail.com'),
       ('John', 'Travolta', 'WhereAmI@cloud.com');

-- Создание таблицы UsersEmailHistory
CREATE TABLE test.Users_1EmailHistory
(
    log_id     serial,
    user_id    INT,
    old_email  VARCHAR(40),
    new_email  VARCHAR(40),
    updated_on DATE
);



create or replace function test.Users_1EmailHistory_log()
returns trigger as 
$$
	begin 
		insert into test.Users_1EmailHistory (user_id, old_email, new_email, updated_on)
		VALUES(old.id, old.email, new.email, current_date);
		return new;
	end;
$$ language plpgsql;

create trigger Users_1EmailHistory_log
	before update
	on test.Users_1
	for each row
	execute function Users_1EmailHistory_log();



-- создание тригерной функции для подсчета потраченных денег на фильмы --
DROP TABLE IF EXISTS test.Purchases;
DROP TABLE IF EXISTS test.Users;
DROP TABLE IF EXISTS test.Films;


-- Создание таблицы Films
CREATE TABLE test.Films
(
    id       serial,
    title    VARCHAR(20),
    director VARCHAR(20),
    price    DECIMAL(5, 2)
);

INSERT INTO test.Films (title, director, price)
VALUES ('Toy Story 2', 'John Lasseter', 2.99),
       ('WALL-E', 'Andrew Stanton', 4.99),
       ('Ratatouille', 'Brad Bird', 4.99),
       ('Up', 'Pete Docter', 4.99),
       ('Brave', 'Brenda Chapman', 7.99),
       ('Monsters University', 'Dan Scanlon', 7.99),
       ('Cars 2', 'John Lasseter', 7.99),
       ('Finding Nemo', 'Andrew Stanton', 4.99),
       ('Toy Story', 'John Lasseter', 2.99),
       ('The Incredibles', 'Brad Bird', 4.99);

-- Создание таблицы Users
CREATE TABLE test.Users
(
    id             serial,
    name           VARCHAR(40),
    surname        VARCHAR(40),
    total_spending DECIMAL(5, 2)
);
INSERT INTO test.Users (name, surname, total_spending)
VALUES ('Matt', 'Damon', 23.96),
       ('Edward', 'Norton', 10.98),
       ('Nicolas', 'Cage', 10.98),
       ('Ben', 'Affleck', 7.98),
       ('John', 'Travolta', 0.0);

-- Создание таблицы Purchases
CREATE TABLE test.Purchases
(
    id      serial,
    film_id INT,
    user_id INT
);
INSERT INTO test.Purchases (film_id, user_id)
VALUES (1, 1),
       (1, 3),
       (2, 4),
       (1, 2),
       (9, 4),
       (6, 1),
       (7, 2),
       (6, 3),
       (5, 1),
       (10, 1);


-- создание тригерной функции, которая подсчитывает расходы на походы в кино--
create or replace function test.total_spending()
returns trigger as 
$$
	declare film_cost float;
	begin
		select test.films.price into film_cost 
			from test.films 
			where test.films.id = new.film_id;

		-- обновляю общие расходы пользователя --
		update test.users
		set total_spending = total_spending + film_cost
		where test.users.id = new.user_id;
		
		return new;
	end;
$$ language plpgsql;

create trigger total_spending_trigger
	before insert
	on test.purchases
	for each row
	execute function test.total_spending();


select test.films.price from test.films where test.films.id = 1;
