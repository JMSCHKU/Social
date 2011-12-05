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
-- Name: googleplus_activitiesaccesses; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE googleplus_activitiesaccesses (
    activities_id character varying(32),
    accesses_id character varying(32)
);


ALTER TABLE public.googleplus_activitiesaccesses OWNER TO jmsc;

--
-- Name: googleplus_activitiesaccesses_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY googleplus_activitiesaccesses
    ADD CONSTRAINT googleplus_activitiesaccesses_pkey PRIMARY KEY (activities_id, accesses_id);


--
-- Name: googleplus_activitiesaccesses_listid_idx; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

---CREATE INDEX googleplus_activitiesaccesses_accessesid_idx ON googleplus_activitiesaccesses USING btree (accesses_id);


--
-- Name: googleplus_activitiesaccesses_list_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jmsc
--

ALTER TABLE ONLY googleplus_activitiesaccesses
    ADD CONSTRAINT googleplus_activitiesaccesses_accesses_id_fkey FOREIGN KEY (accesses_id) REFERENCES googleplus_accesses(id);


--
-- Name: googleplus_activitiesaccesses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jmsc
--

ALTER TABLE ONLY googleplus_activitiesaccesses
    ADD CONSTRAINT googleplus_activitiesaccesses_activities_id_fkey FOREIGN KEY (activities_id) REFERENCES googleplus_activities(id);


--
-- Name: googleplus_activitiesaccesses; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE googleplus_activitiesaccesses FROM PUBLIC;
REVOKE ALL ON TABLE googleplus_activitiesaccesses FROM jmsc;
GRANT ALL ON TABLE googleplus_activitiesaccesses TO jmsc;
GRANT SELECT ON TABLE googleplus_activitiesaccesses TO social_user;


--
-- PostgreSQL database dump complete
--

