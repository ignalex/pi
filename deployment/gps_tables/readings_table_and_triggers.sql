-- readings table 
-- Table: public.readings

-- DROP TABLE public.readings;

CREATE TABLE public.readings
(
  id integer NOT NULL DEFAULT nextval('readings_id_seq'::regclass),
  stamp timestamp without time zone DEFAULT now(),
  lat numeric,
  lon numeric,
  geom geometry,
  delta_seconds double precision,
  distance integer,
  bearing integer,
  speed integer,
  cm_direction integer,
  cm_type character varying,
  cm_speed_limit integer,
  cm_dist integer
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.readings
  OWNER TO pi;

-- Index: public.idx_id

-- DROP INDEX public.idx_id;

CREATE INDEX idx_id
  ON public.readings
  USING btree
  (id);

-- Index: public.idx_stamp

-- DROP INDEX public.idx_stamp;

CREATE INDEX idx_stamp
  ON public.readings
  USING brin
  (stamp);


-- Trigger: make_calcs on public.readings
-- Function: public.make_calcs()

-- DROP FUNCTION public.make_calcs();

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
ALTER FUNCTION public.make_calcs()
  OWNER TO pi;

-- DROP TRIGGER make_calcs ON public.readings;

CREATE TRIGGER make_calcs
  BEFORE INSERT
  ON public.readings
  FOR EACH ROW
  EXECUTE PROCEDURE public.make_calcs();

