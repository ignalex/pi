
-- tab structure 
alter table readings add column delta_seconds double precision; 
create index idx_id on readings (id);

alter table readings add column distance int; 
alter table readings add column bearing int; 
alter table readings add column speed int; 
alter table readings add column cm_type character varying; 
alter table readings add column cm_direction int; 
alter table readings add column cm_speed_limit int; 
alter table readings add column cm_dist int; 

-- calcs 
CREATE OR REPLACE FUNCTION public.make_calcs()
  RETURNS trigger AS
$BODY$
DECLARE 
	LAST_ROW readings%ROWTYPE;
	NEAREST RECORD; 
BEGIN
	select * into LAST_ROW from readings where id = (select max(id) from readings); 

	NEW.geom := st_setsrid(st_makepoint(NEW.lon,NEW.lat),4326); 
	NEW.delta_seconds :=  extract('seconds' from ( NEW.stamp - LAST_ROW.stamp)); 
	NEW.distance := ST_Distance(NEW.geom :: geography, LAST_ROW.geom :: geography) :: int; 
	NEW.bearing := degrees(ST_Azimuth(NEW.geom, LAST_ROW.geom)); 
	NEW.speed := NEW.distance * 3.600 /  NEW.delta_seconds ; -- m/s 2 km/h

	-- nearest cam 
	select 	cm."Camera_DrivingDirection" cm_direction, 
		cm."Camera_CameraType" cm_type, 
		cm."Camera_SpeedLimit" cm_speed_limit, 
		st_distance(cm.geom::geography, NEW.geom::geography) :: int as cm_dist
		into NEAREST
		from geo_routing_2017.cameras cm 
		order by cm.geom <#> NEW.geom
		limit 1; 	

	NEW.cm_direction := NEAREST.cm_direction; 
	NEW.cm_type := NEAREST.cm_type; 
	NEW.cm_speed_limit := NEAREST.cm_speed_limit; 
	NEW.cm_dist := NEAREST.cm_dist; 

RETURN NEW; 
END; 
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE TRIGGER make_calcs
  BEFORE INSERT
  ON public.readings
  FOR EACH ROW
  EXECUTE PROCEDURE public.make_calcs();



-- test 
insert into readings (lon, lat) values (151,-32.2); 
