--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: sinaweibo_provinces; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE sinaweibo_provinces (
    provid smallint NOT NULL,
    cityid smallint NOT NULL,
    provname character varying(16),
    cityname character varying(16),
    name_en character varying(256),
    point geometry,
    bbox geometry,
    CONSTRAINT enforce_dims_bbox CHECK ((st_ndims(bbox) = 2)),
    CONSTRAINT enforce_dims_point CHECK ((st_ndims(point) = 2)),
    CONSTRAINT enforce_geotype_bbox CHECK (((geometrytype(bbox) = 'POLYGON'::text) OR (bbox IS NULL))),
    CONSTRAINT enforce_geotype_point CHECK (((geometrytype(point) = 'POINT'::text) OR (point IS NULL))),
    CONSTRAINT enforce_srid_bbox CHECK ((st_srid(bbox) = 4326)),
    CONSTRAINT enforce_srid_point CHECK ((st_srid(point) = 4326))
);


ALTER TABLE public.sinaweibo_provinces OWNER TO jmsc;

--
-- Name: sinaweibo_provinces_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY sinaweibo_provinces
    ADD CONSTRAINT sinaweibo_provinces_pkey PRIMARY KEY (provid, cityid);


--
-- Name: sinaweibo_provinces; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE sinaweibo_provinces FROM PUBLIC;
REVOKE ALL ON TABLE sinaweibo_provinces FROM jmsc;
GRANT ALL ON TABLE sinaweibo_provinces TO jmsc;
GRANT SELECT ON TABLE sinaweibo_provinces TO social_user;


--
-- PostgreSQL database dump complete
--

