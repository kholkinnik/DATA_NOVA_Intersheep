DROP TABLE IF EXISTS test.Math;
CREATE TABLE test.Math
(
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(20),
    surname VARCHAR(20),
    grade   INT
);

INSERT INTO test.Math (name, surname, grade)
VALUES ('Flash', 'Thompson', 2),
       ('Peter', 'Parker', 5),
       ('Mary', 'Jane', 2),
       ('Gwen', 'Stacy', 4),
       ('Harry', 'Osborn', 5),
       ('Ben', 'Reilly', 1),
       ('Miles', 'Morales', 5),
       ('John', 'Jameson', 1),
       ('Curtis', 'Connors', 4),
       ('Edward', 'Brock', 3);

-- функция для опрделения четности --
CREATE or replace FUNCTION test.IS_EVEN(number INT)
RETURNS varchar
language plpgsql
as $$
	BEGIN
	    if number % 2 = 0 then
	    	return 'четная';
		elsif number = 193 then
			return '193';
		else 
			return 'не четная';
		end if;
	end;
$$;

COMMENT ON FUNCTION test.IS_EVEN IS 'Функция определяет четность числа';

SELECT test.IS_EVEN(10),
       test.IS_EVEN(193);

-- функцция по подсчету количества символов не являющихся пробелами -- 
create or replace function test.NON_SPACE_CHARACTERS(string text)
returns text
language plpgsql
as $$
	declare result int;
	begin 
		select LENGTH(REPLACE(string, ' ', '')) into result;
		return concat(result, ' ', 'букв без пробелов');
	end;
$$;

--тесты	
SELECT test.NON_SPACE_CHARACTERS(' Bee   Geek ');
SELECT test.NON_SPACE_CHARACTERS('');
SELECT test.NON_SPACE_CHARACTERS('@#%^^&(())');


-- функция которая возвращает проверку в том что сотоит ли число из одних и тех же цифер
create or replace function test.SAME_DIGITS(number INT)
returns INT
language plpgsql
as $$
	declare first_value VARCHAR(5);
	declare	string VARCHAR(250);
	begin 
		SELECT CAST(number as VARCHAR(250)) INTO string;
		SELECT left(string,1) into first_value;
			if LENGTH(REPLACE(string, first_value, '')) = 0 then 
				return 1;
		 	else 	
				return 0;
			end if;
		
	end;
$$;
	
select test.SAME_DIGITS(30);	

--функуия калькулятор--
create or replace function test.calculate(a float, b float, operation text)
returns float
language plpgsql
as $$
	begin 
		if operation = '+' then
			return a+b;
		elsif operation = '-' then
			return a-b;
		elsif operation = '*' then
			return a*b;
		elsif operation = '/' then
			return a/b;
		end if;
	end;
$$;
--ТЕСТ--
select test.calculate(73.18, -58.88, '/')

-- функция возвращающая последнюю вторую цифру в числе -- 
create or replace function test.LAST_SECOND_DIGIT(number INT)
returns INT
language plpgsql
as $$
	begin
		if length (cast(number as varchar)) = 1 then
			return null;
		else 
			return cast(left(right(cast(number as varchar), 2),1) as INT);
		end if;
	end;
$$;

--тест--
select test.LAST_SECOND_DIGIT(123485)

-- функция TOTAl(), возвращающая общую сумму заказов по магазину --

--создание БД--
DROP TABLE IF EXISTS test.Orders;
CREATE TABLE test.Orders
(
    id         SERIAL PRIMARY key,
    store      VARCHAR(40),
    amount     INT
);

INSERT INTO test.Orders (store, amount)
VALUES ('Ozon', 101),
       ('PCUniverse', 799),
       ('PCUniverse', 99),
       ('DarkStore', 99),
       ('DarkStore', 1015),
       ('Ozon', 678),
       ('PCUniverse', 858),
       ('Ozon', 458),
       ('Ozon', 801),
       ('DarkStore', 325);

create or replace function test.total(store_name varchar)
returns INT
language plpgsql
as $$ 
declare result INT;
	begin
		select COALESCE(sum(amount),0)
		INTO result
		from test.Orders 
		WHERE store = store_name;	
	return result;
end;
$$;

--тест --
SELECT test.total('PCUniverse');
select sum(amount) from test.Orders group by store having store = 'Ozon';