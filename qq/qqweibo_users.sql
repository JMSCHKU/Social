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
-- Name: qqweibo_users; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE qqweibo_users (
    retrieved timestamp without time zone DEFAULT now(),
    name character varying(64) NOT NULL,
    openid character varying(64),
    nick character varying(64) NOT NULL,
    head character varying(128),
    location character varying(64),
    country_code integer,
    province_code integer,
    city_code integer,
    isvip smallint,
    isent smallint,
    introduction character varying(256),
    verifyinfo character varying(256),
    email character varying(128),
    birth_year integer,
    birth_month integer,
    birth_day integer,
    sex smallint,
    fansnum integer,
    idolnum integer,
    tweetnum integer,
    posts_updated timestamp without time zone,
    deleted timestamp without time zone,
    last_post_date timestamp without time zone
);


ALTER TABLE public.qqweibo_users OWNER TO jmsc;

--
-- Name: qqweibo_users_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY qqweibo_users
    ADD CONSTRAINT qqweibo_users_pkey PRIMARY KEY (name);


--
-- Name: qqweibo_users_city_code_idx; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE INDEX qqweibo_users_city_code_idx ON qqweibo_users USING hash (city_code);


--
-- Name: qqweibo_users_country_code_idx; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE INDEX qqweibo_users_country_code_idx ON qqweibo_users USING hash (country_code);


--
-- Name: qqweibo_users_fansnum_idx; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE INDEX qqweibo_users_fansnum_idx ON qqweibo_users USING btree (fansnum DESC);


--
-- Name: qqweibo_users_province_code_idx; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE INDEX qqweibo_users_province_code_idx ON qqweibo_users USING hash (province_code);


--
-- Name: qqweibo_users; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE qqweibo_users FROM PUBLIC;
REVOKE ALL ON TABLE qqweibo_users FROM jmsc;
GRANT ALL ON TABLE qqweibo_users TO jmsc;
GRANT SELECT ON TABLE qqweibo_users TO social_user;


--
-- PostgreSQL database dump complete
--

