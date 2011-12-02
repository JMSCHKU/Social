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
-- Name: qqweibo_usertags; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE qqweibo_usertags (
    user_name character varying(64) NOT NULL,
    tag_id character varying(64) NOT NULL
);


ALTER TABLE public.qqweibo_usertags OWNER TO jmsc;

--
-- Name: qqweibo_usertags_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY qqweibo_usertags
    ADD CONSTRAINT qqweibo_usertags_pkey PRIMARY KEY (user_name, tag_id);


--
-- Name: qqweibo_usertags_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jmsc
--

ALTER TABLE ONLY qqweibo_usertags
    ADD CONSTRAINT qqweibo_usertags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES qqweibo_tags(id);


--
-- Name: qqweibo_usertags_user_name_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jmsc
--

ALTER TABLE ONLY qqweibo_usertags
    ADD CONSTRAINT qqweibo_usertags_user_name_fkey FOREIGN KEY (user_name) REFERENCES qqweibo_users(name);


--
-- Name: qqweibo_usertags; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE qqweibo_usertags FROM PUBLIC;
REVOKE ALL ON TABLE qqweibo_usertags FROM jmsc;
GRANT ALL ON TABLE qqweibo_usertags TO jmsc;
GRANT SELECT ON TABLE qqweibo_usertags TO social_user;


--
-- PostgreSQL database dump complete
--

