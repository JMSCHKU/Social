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
    lang character varying(16),
    online_status smallint
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
-- Name: rp_sinaweibo; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE rp_sinaweibo (
    id bigint NOT NULL,
    created_at timestamp without time zone,
    text text,
    in_reply_to_user_id bigint,
    in_reply_to_screen_name character varying(25),
    in_reply_to_status_id bigint,
    screen_name character varying(25),
    user_id bigint,
    truncated boolean,
    thumbnail_pic character varying(256),
    bmiddle_pic character varying(256),
    original_pic character varying(256),
    source character varying(256),
    geo geometry,
    retweeted_status bigint,
    deleted timestamp without time zone,
    dbinserted timestamp without time zone DEFAULT now(),
    reposts_count integer,
    comments_count integer,
    mlevel smallint,
    retweeted_status_user_id bigint,
    permission_denied boolean,
    deleted_last_seen timestamp without time zone
);


ALTER TABLE public.rp_sinaweibo OWNER TO jmsc;

--
-- Name: sinaweibo_insert_trigger; Type: TRIGGER; Schema: public; Owner: jmsc
--

CREATE TRIGGER sinaweibo_insert_trigger
    BEFORE INSERT ON rp_sinaweibo
    FOR EACH ROW
    EXECUTE PROCEDURE sinaweibo_insert_function();


--
-- Name: rp_sinaweibo; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE rp_sinaweibo FROM PUBLIC;
REVOKE ALL ON TABLE rp_sinaweibo FROM jmsc;
GRANT ALL ON TABLE rp_sinaweibo TO jmsc;
GRANT SELECT ON TABLE rp_sinaweibo TO social_user;


--
-- PostgreSQL database dump complete
--

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
-- Name: sinaweibo_provinces; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE sinaweibo_provinces (
    provid smallint NOT NULL,
    cityid smallint NOT NULL,
    provname character varying(16),
    cityname character varying(16),
    name_en character varying(256),
    point geometry,
    bbox geometry,
    CONSTRAINT enforce_dims_bbox CHECK ((st_ndims(bbox) = 2)),
    CONSTRAINT enforce_dims_point CHECK ((st_ndims(point) = 2)),
    CONSTRAINT enforce_geotype_bbox CHECK (((geometrytype(bbox) = 'POLYGON'::text) OR (bbox IS NULL))),
    CONSTRAINT enforce_geotype_point CHECK (((geometrytype(point) = 'POINT'::text) OR (point IS NULL))),
    CONSTRAINT enforce_srid_bbox CHECK ((st_srid(bbox) = 4326)),
    CONSTRAINT enforce_srid_point CHECK ((st_srid(point) = 4326))
);


ALTER TABLE public.sinaweibo_provinces OWNER TO jmsc;

--
-- Name: sinaweibo_provinces_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY sinaweibo_provinces
    ADD CONSTRAINT sinaweibo_provinces_pkey PRIMARY KEY (provid, cityid);


--
-- Name: sinaweibo_provinces; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE sinaweibo_provinces FROM PUBLIC;
REVOKE ALL ON TABLE sinaweibo_provinces FROM jmsc;
GRANT ALL ON TABLE sinaweibo_provinces TO jmsc;
GRANT SELECT ON TABLE sinaweibo_provinces TO social_user;


--
-- PostgreSQL database dump complete
--

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
-- Name: sinaweibo_emotions; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE sinaweibo_emotions (
    phrase character varying(16) NOT NULL,
    type character varying(16) NOT NULL,
    url character varying(256) NOT NULL,
    is_hot boolean NOT NULL,
    is_common boolean NOT NULL,
    order_number integer DEFAULT 0 NOT NULL,
    category character varying(16) DEFAULT ''::character varying NOT NULL,
    locale character(2) NOT NULL,
    equiv character varying(16)
);


ALTER TABLE public.sinaweibo_emotions OWNER TO jmsc;

--
-- Name: sinaweibo_emotions_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY sinaweibo_emotions
    ADD CONSTRAINT sinaweibo_emotions_pkey PRIMARY KEY (phrase, type, locale, category);


--
-- PostgreSQL database dump complete
--

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
-- Name: sinaweibo_sinaurl; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE sinaweibo_sinaurl (
    hash character varying(16) NOT NULL,
    location character varying(512),
    base character varying(16) NOT NULL,
    dbinserted timestamp without time zone DEFAULT now()
);


ALTER TABLE public.sinaweibo_sinaurl OWNER TO jmsc;

--
-- Name: sinaweibo_sinaurl_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY sinaweibo_sinaurl
    ADD CONSTRAINT sinaweibo_sinaurl_pkey PRIMARY KEY (base, hash);


--
-- PostgreSQL database dump complete
--

