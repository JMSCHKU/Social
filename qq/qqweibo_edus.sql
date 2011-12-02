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
-- Name: qqweibo_edus; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE qqweibo_edus (
    id integer NOT NULL,
    name character varying(256),
    departmentid integer,
    schoolid integer,
    level smallint
);


ALTER TABLE public.qqweibo_edus OWNER TO jmsc;

--
-- Name: qqweibo_edus_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY qqweibo_edus
    ADD CONSTRAINT qqweibo_edus_pkey PRIMARY KEY (id);


--
-- Name: qqweibo_edus; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE qqweibo_edus FROM PUBLIC;
REVOKE ALL ON TABLE qqweibo_edus FROM jmsc;
GRANT ALL ON TABLE qqweibo_edus TO jmsc;
GRANT SELECT ON TABLE qqweibo_edus TO social_user;


--
-- PostgreSQL database dump complete
--

