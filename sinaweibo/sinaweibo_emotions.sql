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
-- Name: sinaweibo_emotions; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE sinaweibo_emotions (
    phrase character varying(16) NOT NULL,
    type character varying(16) NOT NULL,
    url character varying(256) NOT NULL,
    is_hot boolean NOT NULL,
    is_common boolean NOT NULL,
    order_number integer DEFAULT 0 NOT NULL,
    category character varying(16) DEFAULT ''::character varying NOT NULL,
    locale character(2) NOT NULL,
    equiv character varying(16)
);


ALTER TABLE public.sinaweibo_emotions OWNER TO jmsc;

--
-- Name: sinaweibo_emotions_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY sinaweibo_emotions
    ADD CONSTRAINT sinaweibo_emotions_pkey PRIMARY KEY (phrase, type, locale, category);


--
-- PostgreSQL database dump complete
--

