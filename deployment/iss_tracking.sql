/* 
deployment of the initial tables for ISS scanning 
to be run only onece for DB 
*/ 

CREATE TABLE public.iss_position
(
  index serial,
  "timestamp" timestamp without time zone,
  latitude double precision,
  longitude double precision,
  velocity double precision,
  altitude double precision,
  how_far bigint, 
  geom geometry
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.iss_position
  OWNER TO pi;

-- Index: public.ix_iss_position_index

-- DROP INDEX public.ix_iss_position_index;

CREATE INDEX ix_iss_position_index
  ON public.iss_position
  USING btree
  (index);


CREATE INDEX six_iss_position_index
  ON public.iss_position
  USING gist
  (geom);

-- triggers for geom 
CREATE OR REPLACE FUNCTION public.iss_geom()
  RETURNS trigger AS
$BODY$
DECLARE 
BEGIN
	NEW.geom := st_setsrid(st_makepoint(NEW.longitude,NEW.latitude),4326); 

RETURN NEW; 
END; 
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION public.iss_geom()
  OWNER TO pi;

-- DROP TRIGGER make_calcs ON public.readings;

CREATE TRIGGER iss_geom
  BEFORE INSERT
  ON public.iss_position
  FOR EACH ROW
  EXECUTE PROCEDURE public.iss_geom();

