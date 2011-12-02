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
-- Name: googleplus_organizations; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE googleplus_organizations (
    id character varying(32) DEFAULT nextval('googleplus_organizations_gid_seq'::regclass) NOT NULL,
    dbinserted timestamp without time zone DEFAULT now(),
    parent_id character varying(32) NOT NULL,
    parent_type character varying(32) NOT NULL,
    name character varying(64) NOT NULL,
    department character varying(64),
    title character varying(64),
    startdate character varying(32),
    enddate character varying(32),
    location character varying(64),
    description character varying(512),
    type character varying(32) NOT NULL,
    is_primary boolean
);


ALTER TABLE public.googleplus_organizations OWNER TO jmsc;

--
-- Name: googleplus_organizations_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY googleplus_organizations
    ADD CONSTRAINT googleplus_organizations_pkey PRIMARY KEY (id);


--
-- Name: googleplus_organizations; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE googleplus_organizations FROM PUBLIC;
REVOKE ALL ON TABLE googleplus_organizations FROM jmsc;
GRANT ALL ON TABLE googleplus_organizations TO jmsc;
GRANT SELECT ON TABLE googleplus_organizations TO social_user;


--
-- PostgreSQL database dump complete
--

