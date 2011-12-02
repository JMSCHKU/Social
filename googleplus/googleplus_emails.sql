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
-- Name: googleplus_emails; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE googleplus_emails (
    id character varying(32) DEFAULT nextval('googleplus_emails_gid_seq'::regclass) NOT NULL,
    dbinserted timestamp without time zone DEFAULT now(),
    parent_id character varying(32) NOT NULL,
    parent_type character varying(32) NOT NULL,
    value character varying(64) NOT NULL,
    type character varying(32),
    is_primary boolean
);


ALTER TABLE public.googleplus_emails OWNER TO jmsc;

--
-- Name: googleplus_emails_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY googleplus_emails
    ADD CONSTRAINT googleplus_emails_pkey PRIMARY KEY (id);


--
-- Name: googleplus_emails; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE googleplus_emails FROM PUBLIC;
REVOKE ALL ON TABLE googleplus_emails FROM jmsc;
GRANT ALL ON TABLE googleplus_emails TO jmsc;
GRANT SELECT ON TABLE googleplus_emails TO social_user;


--
-- PostgreSQL database dump complete
--

