
-- with sub as (select now() - stamp as age, distance, speed, bearing, geom from readings order by id desc limit 1) 
select 	cm."Camera_DrivingDirection" cm_direction, 
	cm."Camera_CameraType" cm_type, 
	cm."Camera_SpeedLimit" cm_speed_limit, 
	st_distance(cm.geom::geography, sub.geom::geography) :: int as dist, 
	sub.speed, 
	sub.bearing, 
	sub.age from geo_routing_2017.cameras cm, 
	(select now() - stamp as age, distance, speed, bearing, geom from readings order by id desc limit 1) sub 
	order by cm.geom <#> sub.geom
	limit 1; 

create or replace function current() 
returns TABLE (cm_direction int, cm_type character varying, cm_speed_limit int, dist int, speed int, bearing int, age interval)
as 
$$
select 	cm."Camera_DrivingDirection" cm_direction, 
	cm."Camera_CameraType" cm_type, 
	cm."Camera_SpeedLimit" cm_speed_limit, 
	st_distance(cm.geom::geography, sub.geom::geography) :: int as dist, 
	sub.speed, 
	sub.bearing, 
	sub.age from geo_routing_2017.cameras cm, 
	(select now() - stamp as age, distance, speed, bearing, geom from readings order by id desc limit 1) sub 
	order by cm.geom <#> sub.geom
	limit 1; 
$$
  LANGUAGE sql IMMUTABLE STRICT
  COST 100
  ROWS 1;

select cm_direction , cm_type  , cm_speed_limit , dist , speed , bearing , age from current(); 


create table readings_calcs  (
	id serial, 
	cm_direction int, 
	cm_type character varying, 
	cm_speed_limit int, 
	dist int, 
	speed int, 
	bearing int, 
	age interval
) ; 

insert into readings_calcs (cm_direction,cm_type,cm_speed_limit,dist,speed,bearing,age ) select * from current(); 