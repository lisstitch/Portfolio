SET search_path TO bookings;

--Задание №1
--В каких городах больше одного аэропорта?

select a.city
from airports a
group by a.city
having count(a.city) > 1

--Задание №2
--В каких аэропортах есть рейсы, выполняемые самолетом с максимальной дальностью перелета?

select f.departure_airport as airport_code, f.aircraft_code
from flights f
where f.aircraft_code in (
	select ac.aircraft_code
	from aircrafts ac
	order by ac."range" desc
	limit 1
 )
group by 1, 2


--Задание №3
--Вывести 10 рейсов с максимальным временем задержки вылета

select f.flight_id, f.flight_no, f.actual_departure - f.scheduled_departure as delay
from flights f
where f.status = 'Arrived' or f.status = 'Departed'
order by 3 desc
limit 10


--Задание №4
--Были ли брони, по которым не были получены посадочные талоны?

select b.book_ref
from bookings b 
join tickets t on b.book_ref = t.book_ref
left join boarding_passes bp on t.ticket_no = bp.ticket_no
where bp.boarding_no is null

--Задание №5
--Найдите количество свободных мест для каждого рейса, 
--их % отношение к общему количеству мест в самолете. 
--Добавьте столбец с накопительным итогом - суммарное накопление количества
--вывезенных пассажиров из каждого аэропорта на каждый день.
--Т.е. в этом столбце должна отражаться накопительная сумма - сколько человек
--уже вылетело из данного аэропорта на этом или более ранних рейсах в течении дня

with cte1 as (
	select f.flight_id, count(s.seat_no) as "count_seats"
	from flights f
	join seats s on f.aircraft_code = s.aircraft_code 
	group by 1),
cte2 as (
	select f.flight_id, count(bp.boarding_no) as "count_boarding"
	from flights f
	left join boarding_passes bp on f.flight_id = bp.flight_id 
	group by 1)
select f.flight_id, c1.count_seats - c2.count_boarding as "free seats",
round((c1.count_seats - c2.count_boarding) * 100 / c1.count_seats) as percentage,
f.departure_airport,
f.actual_departure,
sum(c2.count_boarding) over (partition by f.departure_airport, date_trunc('day', f.actual_departure) order by f.actual_departure) as departed_passengers
from flights f
join cte1 c1 on f.flight_id = c1.flight_id
join cte2 c2 on c1.flight_id = c2.flight_id
order by f.departure_airport, f.actual_departure

--Задание №6
--Найдите процентное соотношение перелетов по типам самолетов от общего количества

select f.aircraft_code, round(count(f.flight_id) * 100 / sum(count(f.flight_id)) over (), 0) as percentage
from flights f
group by 1

--Задание №7
--Были ли города,
--в которые можно добраться бизнес - классом дешевле,
--чем эконом-классом в рамках перелета?

with cte1 as (
	select tf.flight_id, tf.amount as amount1
	from ticket_flights tf
	where tf.fare_conditions = 'Economy' 
	group by 1, 2),
cte2 as (
	select tfs.flight_id, tfs.amount as amount2
	from ticket_flights tfs
	where tfs.fare_conditions = 'Business'
	group by 1, 2)
select a.city
from airports a
join flights f on a.airport_code = f.arrival_airport
join cte1 c1 on f.flight_id = c1.flight_id
join cte2 c2 on c1.flight_id = c2.flight_id
where c1.amount1 > c2.amount2


--Задание №8
--Между какими городами нет прямых рейсов?

create view flights_view as
	select f.flight_id,
    f.flight_no,
    f.departure_airport,
    dep.airport_name as departure_airport_name,
    dep.city as departure_city,
    f.arrival_airport,
    arr.airport_name as arrival_airport_name,
    arr.city as arrival_city
	from flights f,
    airports dep,
    airports arr
	where f.departure_airport = dep.airport_code and f.arrival_airport = arr.airport_code

select a1.city, a2.city
from airports a1 cross join airports a2
where a1.city != a2.city
except 
select departure_city, arrival_city
from flights_view

--Задание №9
--	Вычислите расстояние между аэропортами, 
--связанными прямыми рейсами,
--сравните с допустимой максимальной дальностью
--перелетов в самолетах, обслуживающих эти рейсы*


select dep.city as departure_city, arr.city as arrival_city, ac."range",
	acos(sind(dep.latitude) * sind(arr.latitude) + cosd(dep.latitude) * cosd(arr.latitude) * cosd(dep.longitude - arr.longitude)) * 6371 as distance,
	case
		when ac."range" >= acos(sind(dep.latitude) * sind(arr.latitude) + cosd(dep.latitude) * cosd(arr.latitude) * cosd(dep.longitude - arr.longitude)) * 6371
		then 'YES'
		else 'NO'
	end as possibility
from flights f
join airports dep on f.departure_airport = dep.airport_code
join airports arr on f.arrival_airport = arr.airport_code
join aircrafts ac on f.aircraft_code = ac.aircraft_code
group by 1, 2, 3, 4


