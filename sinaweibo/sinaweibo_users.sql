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
-- Name: sinaweibo_users; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE sinaweibo_users (
    retrieved timestamp without time zone,
    id bigint NOT NULL,
    name character varying(64),
    screen_name character varying(64) NOT NULL,
    province smallint,
    city smallint,
    location character varying(64),
    description character varying(512),
    profile_image_url character varying(256),
    url character varying(256),
    domain character varying(256),
    gender character(1),
    followers_count bigint,
    friends_count bigint,
    created_at timestamp without time zone,
    favourites_count integer,
    time_zone character varying(128),
    profile_background_image_url character varying(256),
    profile_use_background_image boolean,
    allow_all_act_msg boolean,
    geo_enabled boolean,
    verified boolean,
    following boolean,
    statuses_count bigint,
    posts_updated timestamp without time zone,
    deleted timestamp without time zone,
    last_post_date timestamp without time zone,
    allow_all_comment boolean,
    avatar_large character varying(256),
    verified_reason character varying(256),
    bi_followers_count integer,
    verified_type smallint,
    lang character varying(16)
);


ALTER TABLE public.sinaweibo_users OWNER TO jmsc;

--
-- Name: sinaweibo_users_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY sinaweibo_users
    ADD CONSTRAINT sinaweibo_users_pkey PRIMARY KEY (id);


--
-- Name: sinaweibo_users_city_idx; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE INDEX sinaweibo_users_city_idx ON sinaweibo_users USING hash (city);


--
-- Name: sinaweibo_users_followers_idx; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE INDEX sinaweibo_users_followers_idx ON sinaweibo_users USING btree (followers_count DESC);


--
-- Name: sinaweibo_users_last_post_date_idx; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE INDEX sinaweibo_users_last_post_date_idx ON sinaweibo_users USING btree (last_post_date);


--
-- Name: sinaweibo_users_posts_updated_idx; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE INDEX sinaweibo_users_posts_updated_idx ON sinaweibo_users USING btree (posts_updated);


--
-- Name: sinaweibo_users_province_idx; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE INDEX sinaweibo_users_province_idx ON sinaweibo_users USING hash (province);


--
-- Name: sinaweibo_users; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE sinaweibo_users FROM PUBLIC;
REVOKE ALL ON TABLE sinaweibo_users FROM jmsc;
GRANT ALL ON TABLE sinaweibo_users TO jmsc;
GRANT SELECT ON TABLE sinaweibo_users TO social_user;


--
-- PostgreSQL database dump complete
--

