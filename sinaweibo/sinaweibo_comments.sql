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
-- Name: sinaweibo_comments; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE sinaweibo_comments (
    id bigint NOT NULL,
    created_at timestamp without time zone,
    text text,
    user_id bigint NOT NULL,
    status_id bigint NOT NULL,
    idx_text_fti pg_catalog.tsvector
);


ALTER TABLE public.sinaweibo_comments OWNER TO jmsc;

--
-- Name: sinaweibo_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY sinaweibo_comments
    ADD CONSTRAINT sinaweibo_comments_pkey PRIMARY KEY (id);


--
-- Name: sinaweibo_comments_created_at_idx; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE INDEX sinaweibo_comments_created_at_idx ON sinaweibo_comments USING btree (created_at);


--
-- Name: sinaweibo_comments_idx_text_fti_idx; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE INDEX sinaweibo_comments_idx_text_fti_idx ON sinaweibo_comments USING gist (idx_text_fti);


--
-- Name: sinaweibo_comments_status_id_idx; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE INDEX sinaweibo_comments_status_id_idx ON sinaweibo_comments USING btree (status_id);


--
-- Name: sinaweibo_comments_user_id_idx; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE INDEX sinaweibo_comments_user_id_idx ON sinaweibo_comments USING btree (user_id);


--
-- Name: tsvectorupdate; Type: TRIGGER; Schema: public; Owner: jmsc
--

CREATE TRIGGER tsvectorupdate
    BEFORE INSERT OR UPDATE ON sinaweibo_comments
    FOR EACH ROW
    EXECUTE PROCEDURE tsearch2('idx_text_fti', 'text');


--
-- PostgreSQL database dump complete
--

