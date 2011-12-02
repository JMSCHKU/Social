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
-- Name: sinaweibo_usertags; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE sinaweibo_usertags (
    user_id bigint NOT NULL,
    tag_id bigint NOT NULL
);


ALTER TABLE public.sinaweibo_usertags OWNER TO jmsc;

--
-- Name: sinaweibo_usertags_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY sinaweibo_usertags
    ADD CONSTRAINT sinaweibo_usertags_pkey PRIMARY KEY (user_id, tag_id);


--
-- Name: sinaweibo_usertags_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jmsc
--

ALTER TABLE ONLY sinaweibo_usertags
    ADD CONSTRAINT sinaweibo_usertags_user_id_fkey FOREIGN KEY (user_id) REFERENCES sinaweibo_users(id);


--
-- Name: sinaweibo_usertags; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE sinaweibo_usertags FROM PUBLIC;
REVOKE ALL ON TABLE sinaweibo_usertags FROM jmsc;
GRANT ALL ON TABLE sinaweibo_usertags TO jmsc;
GRANT SELECT ON TABLE sinaweibo_usertags TO social_user;


--
-- PostgreSQL database dump complete
--

