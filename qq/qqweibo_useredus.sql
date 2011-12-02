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
-- Name: qqweibo_useredus; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE qqweibo_useredus (
    user_name character varying(64) NOT NULL,
    edu_id smallint NOT NULL
);


ALTER TABLE public.qqweibo_useredus OWNER TO jmsc;

--
-- Name: qqweibo_useredus_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY qqweibo_useredus
    ADD CONSTRAINT qqweibo_useredus_pkey PRIMARY KEY (user_name, edu_id);


--
-- Name: qqweibo_useredus_edu_id; Type: FK CONSTRAINT; Schema: public; Owner: jmsc
--

ALTER TABLE ONLY qqweibo_useredus
    ADD CONSTRAINT qqweibo_useredus_edu_id FOREIGN KEY (edu_id) REFERENCES qqweibo_edus(id);


--
-- Name: qqweibo_useredus_user_name_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jmsc
--

ALTER TABLE ONLY qqweibo_useredus
    ADD CONSTRAINT qqweibo_useredus_user_name_fkey FOREIGN KEY (user_name) REFERENCES qqweibo_users(name);


--
-- Name: qqweibo_useredus; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE qqweibo_useredus FROM PUBLIC;
REVOKE ALL ON TABLE qqweibo_useredus FROM jmsc;
GRANT ALL ON TABLE qqweibo_useredus TO jmsc;
GRANT SELECT ON TABLE qqweibo_useredus TO social_user;


--
-- PostgreSQL database dump complete
--

