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
-- Name: qqweibo_tags; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE qqweibo_tags (
    id character varying(32) NOT NULL,
    name character varying(256) NOT NULL
);


ALTER TABLE public.qqweibo_tags OWNER TO jmsc;

--
-- Name: qqweibo_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY qqweibo_tags
    ADD CONSTRAINT qqweibo_tags_pkey PRIMARY KEY (id);


--
-- Name: qqweibo_tags; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE qqweibo_tags FROM PUBLIC;
REVOKE ALL ON TABLE qqweibo_tags FROM jmsc;
GRANT ALL ON TABLE qqweibo_tags TO jmsc;
GRANT SELECT ON TABLE qqweibo_tags TO social_user;


--
-- PostgreSQL database dump complete
--

