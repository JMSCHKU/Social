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
-- Name: googleplus_placeslived; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE googleplus_placeslived (
    id character varying(32) DEFAULT nextval('googleplus_placeslived_gid_seq'::regclass) NOT NULL,
    dbinserted timestamp without time zone DEFAULT now(),
    parent_id character varying(32) NOT NULL,
    parent_type character varying(32) NOT NULL,
    value character varying(64) NOT NULL,
    is_primary boolean
);


ALTER TABLE public.googleplus_placeslived OWNER TO jmsc;

--
-- Name: googleplus_placeslived_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY googleplus_placeslived
    ADD CONSTRAINT googleplus_placeslived_pkey PRIMARY KEY (id);


--
-- Name: googleplus_placeslived; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE googleplus_placeslived FROM PUBLIC;
REVOKE ALL ON TABLE googleplus_placeslived FROM jmsc;
GRANT ALL ON TABLE googleplus_placeslived TO jmsc;
GRANT SELECT ON TABLE googleplus_placeslived TO social_user;


--
-- PostgreSQL database dump complete
--

