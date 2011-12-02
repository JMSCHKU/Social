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
-- Name: sinaweibo_userlist; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE sinaweibo_userlist (
    user_id bigint NOT NULL,
    list_id smallint NOT NULL
);


ALTER TABLE public.sinaweibo_userlist OWNER TO jmsc;

--
-- Name: sinaweibo_userlist_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY sinaweibo_userlist
    ADD CONSTRAINT sinaweibo_userlist_pkey PRIMARY KEY (user_id, list_id);


--
-- Name: sinaweibo_userlist_listid_idx; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE INDEX sinaweibo_userlist_listid_idx ON sinaweibo_userlist USING btree (list_id);


--
-- Name: sinaweibo_userlist_list_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jmsc
--

ALTER TABLE ONLY sinaweibo_userlist
    ADD CONSTRAINT sinaweibo_userlist_list_id_fkey FOREIGN KEY (list_id) REFERENCES sinaweibo_mylists(id);


--
-- Name: sinaweibo_userlist_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jmsc
--

ALTER TABLE ONLY sinaweibo_userlist
    ADD CONSTRAINT sinaweibo_userlist_user_id_fkey FOREIGN KEY (user_id) REFERENCES sinaweibo_users(id);


--
-- Name: sinaweibo_userlist; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE sinaweibo_userlist FROM PUBLIC;
REVOKE ALL ON TABLE sinaweibo_userlist FROM jmsc;
GRANT ALL ON TABLE sinaweibo_userlist TO jmsc;
GRANT SELECT ON TABLE sinaweibo_userlist TO social_user;


--
-- PostgreSQL database dump complete
--

