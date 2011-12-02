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
-- Name: sinaweibo_tags; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE sinaweibo_tags (
    id bigint NOT NULL,
    value character varying(256) NOT NULL,
    value_en character varying(256)
);


ALTER TABLE public.sinaweibo_tags OWNER TO jmsc;

--
-- Name: sinaweibo_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY sinaweibo_tags
    ADD CONSTRAINT sinaweibo_tags_pkey PRIMARY KEY (id);


--
-- Name: sinaweibo_tags; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE sinaweibo_tags FROM PUBLIC;
REVOKE ALL ON TABLE sinaweibo_tags FROM jmsc;
GRANT ALL ON TABLE sinaweibo_tags TO jmsc;
GRANT SELECT ON TABLE sinaweibo_tags TO social_user;


--
-- PostgreSQL database dump complete
--

