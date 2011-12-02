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
-- Name: sinaweibo_sinaurl; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE sinaweibo_sinaurl (
    hash character varying(16) NOT NULL,
    location character varying(512),
    base character varying(16) NOT NULL,
    dbinserted timestamp without time zone DEFAULT now()
);


ALTER TABLE public.sinaweibo_sinaurl OWNER TO jmsc;

--
-- Name: sinaweibo_sinaurl_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY sinaweibo_sinaurl
    ADD CONSTRAINT sinaweibo_sinaurl_pkey PRIMARY KEY (base, hash);


--
-- PostgreSQL database dump complete
--

