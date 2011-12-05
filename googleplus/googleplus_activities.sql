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
-- Name: googleplus_activities; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE googleplus_activities (
    id character varying(32) NOT NULL,
    dbinserted timestamp without time zone DEFAULT now() NOT NULL,
    kind character varying(32) NOT NULL,
    title character varying(256) NOT NULL,
    published timestamp without time zone,
    updated timestamp without time zone,
    url character varying(256),
    actor_id character varying(32),
    verb character varying(32),
    objecttype character varying(32),
    crosspostsource character varying(64),
    provider_title character varying(64),
    access_kind character varying(32),
    address character varying(256),
    placeid character varying(32),
    placename character varying(64)
);


ALTER TABLE public.googleplus_activities OWNER TO jmsc;

--
-- Name: googleplus_activities; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE googleplus_activities FROM PUBLIC;
REVOKE ALL ON TABLE googleplus_activities FROM jmsc;
GRANT ALL ON TABLE googleplus_activities TO jmsc;
GRANT SELECT ON TABLE googleplus_activities TO social_user;


--
-- PostgreSQL database dump complete
--

