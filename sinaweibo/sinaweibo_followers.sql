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
-- Name: sinaweibo_followers; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE sinaweibo_followers (
    source_id bigint NOT NULL,
    target_id bigint NOT NULL,
    retrieved timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.sinaweibo_followers OWNER TO jmsc;

--
-- Name: sinaweibo_followers_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY sinaweibo_followers
    ADD CONSTRAINT sinaweibo_followers_pkey PRIMARY KEY (source_id, target_id);


--
-- Name: sinaweibo_followers_source_target; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE UNIQUE INDEX sinaweibo_followers_source_target ON sinaweibo_followers USING btree (source_id, target_id);


--
-- Name: sinaweibo_followers; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE sinaweibo_followers FROM PUBLIC;
REVOKE ALL ON TABLE sinaweibo_followers FROM jmsc;
GRANT ALL ON TABLE sinaweibo_followers TO jmsc;
GRANT SELECT ON TABLE sinaweibo_followers TO social_user;


--
-- PostgreSQL database dump complete
--

