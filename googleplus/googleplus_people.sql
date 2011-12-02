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
-- Name: googleplus_people; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE googleplus_people (
    id character varying(32) NOT NULL,
    dbinserted timestamp without time zone DEFAULT now() NOT NULL,
    kind character varying(32) NOT NULL,
    displayname character varying(256) NOT NULL,
    url character varying(256),
    image_url character varying(256),
    objecttype character varying(32),
    nickname character varying(64),
    tagline character varying(256),
    birthday character varying(32),
    currentlocation character varying(128),
    relationshipstatus character varying(32),
    hasapp boolean,
    languagesspoken character varying(32)[],
    gender character varying(8),
    aboutme character varying(256)
);


ALTER TABLE public.googleplus_people OWNER TO jmsc;

--
-- Name: googleplus_users_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY googleplus_people
    ADD CONSTRAINT googleplus_users_pkey PRIMARY KEY (id);


--
-- Name: googleplus_people; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE googleplus_people FROM PUBLIC;
REVOKE ALL ON TABLE googleplus_people FROM jmsc;
GRANT ALL ON TABLE googleplus_people TO jmsc;
GRANT SELECT ON TABLE googleplus_people TO social_user;


--
-- PostgreSQL database dump complete
--

