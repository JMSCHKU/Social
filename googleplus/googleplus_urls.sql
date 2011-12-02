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
-- Name: googleplus_urls; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE googleplus_urls (
    id character varying(32) DEFAULT nextval('googleplus_urls_gid_seq'::regclass) NOT NULL,
    dbinserted timestamp without time zone DEFAULT now(),
    parent_id character varying(32) NOT NULL,
    parent_type character varying(32) NOT NULL,
    value character varying(64) NOT NULL,
    type character varying(32),
    is_primary boolean
);


ALTER TABLE public.googleplus_urls OWNER TO jmsc;

--
-- Name: googleplus_urls_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY googleplus_urls
    ADD CONSTRAINT googleplus_urls_pkey PRIMARY KEY (id);


--
-- Name: googleplus_urls; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE googleplus_urls FROM PUBLIC;
REVOKE ALL ON TABLE googleplus_urls FROM jmsc;
GRANT ALL ON TABLE googleplus_urls TO jmsc;
GRANT SELECT ON TABLE googleplus_urls TO social_user;


--
-- PostgreSQL database dump complete
--

