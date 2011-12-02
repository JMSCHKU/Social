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
-- Name: qqweibo_friends; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE qqweibo_friends (
    source_id character varying(64) NOT NULL,
    target_id character varying(64) NOT NULL,
    retrieved timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.qqweibo_friends OWNER TO jmsc;

--
-- Name: qqweibo_friends_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY qqweibo_friends
    ADD CONSTRAINT qqweibo_friends_pkey PRIMARY KEY (source_id, target_id);


--
-- Name: qqweibo_friends_source_target; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE UNIQUE INDEX qqweibo_friends_source_target ON qqweibo_friends USING btree (source_id, target_id);


--
-- Name: qqweibo_friends; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE qqweibo_friends FROM PUBLIC;
REVOKE ALL ON TABLE qqweibo_friends FROM jmsc;
GRANT ALL ON TABLE qqweibo_friends TO jmsc;
GRANT SELECT ON TABLE qqweibo_friends TO social_user;


--
-- PostgreSQL database dump complete
--

