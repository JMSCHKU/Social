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
-- Name: googleplus_activitiesattachments; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE googleplus_activitiesattachments (
    activities_id character varying(32) NOT NULL,
    attachment_url character varying(256) NOT NULL
);


ALTER TABLE public.googleplus_activitiesattachments OWNER TO jmsc;

--
-- Name: googleplus_activitiesattachments_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY googleplus_activitiesattachments
    ADD CONSTRAINT googleplus_activitiesattachments_pkey PRIMARY KEY (activities_id, attachment_url);


--
-- Name: googleplus_activitiesattachments; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE googleplus_activitiesattachments FROM PUBLIC;
REVOKE ALL ON TABLE googleplus_activitiesattachments FROM jmsc;
GRANT ALL ON TABLE googleplus_activitiesattachments TO jmsc;
GRANT SELECT ON TABLE googleplus_activitiesattachments TO social_user;


--
-- PostgreSQL database dump complete
--

