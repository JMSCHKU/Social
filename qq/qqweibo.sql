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
-- Name: qqweibo; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE qqweibo (
    id bigint NOT NULL,
    "timestamp" integer,
    timestamp_now integer,
    text text,
    origtext text,
    count integer,
    mcount integer,
    "from" character varying(32),
    image character varying(256)[],
    name character varying(64),
    openid character varying(64),
    nick character varying(32),
    self integer,
    type smallint,
    head character varying(128),
    location character varying(128),
    country_code smallint,
    province_code smallint,
    city_code smallint,
    isvip smallint,
    geo smallint,
    status smallint,
    video_picurl character varying(256),
    video_player character varying(256),
    video_realurl character varying(256),
    video_shorturl character varying(256),
    video_title character varying(128),
    music_author character varying(64),
    music_url character varying(256),
    music_title character varying(128),
    user_names character varying(64)[],
    user_nicks character varying(32)[],
    deleted timestamp without time zone
);


ALTER TABLE public.qqweibo OWNER TO jmsc;

--
-- Name: qqweibo_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY qqweibo
    ADD CONSTRAINT qqweibo_pkey PRIMARY KEY (id);


--
-- Name: qqweibo; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE qqweibo FROM PUBLIC;
REVOKE ALL ON TABLE qqweibo FROM jmsc;
GRANT ALL ON TABLE qqweibo TO jmsc;
GRANT SELECT ON TABLE qqweibo TO social_user;


--
-- PostgreSQL database dump complete
--

