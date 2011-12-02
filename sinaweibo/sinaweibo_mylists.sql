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
-- Name: sinaweibo_mylists; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE sinaweibo_mylists (
    id integer DEFAULT nextval('sinaweibo_mylists_gid_seq'::regclass) NOT NULL,
    name character varying(256) NOT NULL
);


ALTER TABLE public.sinaweibo_mylists OWNER TO jmsc;

--
-- Name: sinaweibo_mylists_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY sinaweibo_mylists
    ADD CONSTRAINT sinaweibo_mylists_pkey PRIMARY KEY (id);


--
-- Name: sinaweibo_mylists; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE sinaweibo_mylists FROM PUBLIC;
REVOKE ALL ON TABLE sinaweibo_mylists FROM jmsc;
GRANT ALL ON TABLE sinaweibo_mylists TO jmsc;
GRANT SELECT ON TABLE sinaweibo_mylists TO social_user;


--
-- PostgreSQL database dump complete
--

