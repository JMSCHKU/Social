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
-- Name: facebook_applications; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE facebook_applications (
    id bigint NOT NULL,
    name character varying(256),
    description text,
    link character varying(256),
    category character varying(64),
    subcategory character varying(64),
    picture character varying(512),
    retrieved timestamp without time zone DEFAULT now()
);


ALTER TABLE public.facebook_applications OWNER TO jmsc;

--
-- Name: facebook_comments; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE facebook_comments (
    id character varying(64) NOT NULL,
    "from" bigint,
    message text,
    created_time timestamp without time zone,
    pid character varying(64)
);


ALTER TABLE public.facebook_comments OWNER TO jmsc;

--
-- Name: facebook_events; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE facebook_events (
    id bigint NOT NULL,
    picture character varying(512),
    owner bigint,
    name character varying(256),
    description text,
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    location character varying(256),
    venue character varying(256),
    privacy character varying(8),
    updated_time timestamp without time zone,
    retrieved timestamp without time zone DEFAULT now(),
    watching boolean,
    dbinserted timestamp without time zone DEFAULT now()
);


ALTER TABLE public.facebook_events OWNER TO jmsc;

--
-- Name: facebook_events_watch; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE facebook_events_watch (
    eid bigint NOT NULL,
    attending_count integer,
    unsure_count integer,
    declined_count integer,
    notreplied_count integer,
    retrieved timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.facebook_events_watch OWNER TO jmsc;

--
-- Name: facebook_groups; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE facebook_groups (
    id bigint NOT NULL,
    icon character varying(256),
    owner bigint,
    name character varying(256),
    description text,
    link character varying(256),
    privacy character varying(8),
    updated_time timestamp without time zone,
    retrieved timestamp without time zone DEFAULT now(),
    picture character varying(512),
    members_count bigint,
    watching boolean,
    dbinserted timestamp without time zone DEFAULT now()
);


ALTER TABLE public.facebook_groups OWNER TO jmsc;

--
-- Name: facebook_groups_watch; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE facebook_groups_watch (
    gid bigint NOT NULL,
    retrieved timestamp without time zone DEFAULT now() NOT NULL,
    members_count integer
);


ALTER TABLE public.facebook_groups_watch OWNER TO jmsc;

--
-- Name: facebook_likes; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE facebook_likes (
    uid bigint NOT NULL,
    pid character varying(64) NOT NULL
);


ALTER TABLE public.facebook_likes OWNER TO jmsc;

--
-- Name: facebook_mylists_gid_seq; Type: SEQUENCE; Schema: public; Owner: jmsc
--

CREATE SEQUENCE facebook_mylists_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.facebook_mylists_gid_seq OWNER TO jmsc;

--
-- Name: facebook_mylists; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE facebook_mylists (
    id integer DEFAULT nextval('facebook_mylists_gid_seq'::regclass) NOT NULL,
    name character varying(256) NOT NULL
);


ALTER TABLE public.facebook_mylists OWNER TO jmsc;

--
-- Name: facebook_pages; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE facebook_pages (
    id bigint NOT NULL,
    name character varying(256),
    picture character varying(512),
    link character varying(512),
    category character varying(64),
    website character varying(512),
    username character varying(256),
    products text,
    fan_count bigint,
    retrieved timestamp without time zone DEFAULT now(),
    description text,
    founded character varying(256),
    company_overview text,
    mission text,
    subcategory character varying(64),
    watching boolean,
    dbinserted timestamp without time zone DEFAULT now()
);


ALTER TABLE public.facebook_pages OWNER TO jmsc;

--
-- Name: facebook_pages_watch; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE facebook_pages_watch (
    pid bigint NOT NULL,
    retrieved timestamp without time zone DEFAULT now() NOT NULL,
    fan_count integer
);


ALTER TABLE public.facebook_pages_watch OWNER TO jmsc;

--
-- Name: facebook_posts; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE facebook_posts (
    id character varying(64) NOT NULL,
    "from" bigint NOT NULL,
    name character varying(256),
    description text,
    message text,
    caption text,
    picture character varying(512),
    icon character varying(512),
    link character varying(512),
    type character varying(8),
    privacy character varying(8),
    source character varying(512),
    likes bigint,
    comments text,
    comments_count bigint,
    properties text,
    created_time timestamp without time zone,
    updated_time timestamp without time zone,
    retrieved timestamp without time zone DEFAULT now(),
    "to" bigint
);


ALTER TABLE public.facebook_posts OWNER TO jmsc;

--
-- Name: facebook_userlist; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE facebook_userlist (
    obj_id bigint NOT NULL,
    obj_type facebook_type NOT NULL,
    list_id smallint NOT NULL
);


ALTER TABLE public.facebook_userlist OWNER TO jmsc;

--
-- Name: facebook_users; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE facebook_users (
    id bigint NOT NULL,
    name character varying(256) NOT NULL,
    retrieved timestamp without time zone DEFAULT now() NOT NULL,
    first_name character varying(256),
    last_name character varying(256),
    link character varying(256),
    updated_time timestamp without time zone,
    locale character varying(8),
    timezone numeric,
    verified boolean,
    gender character varying(8),
    third_party_id character varying(32)
);


ALTER TABLE public.facebook_users OWNER TO jmsc;

--
-- Name: facebook_users_events; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE facebook_users_events (
    uid bigint NOT NULL,
    eid bigint NOT NULL,
    rsvp_status character varying(16),
    retrieved timestamp without time zone DEFAULT now()
);


ALTER TABLE public.facebook_users_events OWNER TO jmsc;

--
-- Name: facebook_users_groups; Type: TABLE; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE TABLE facebook_users_groups (
    uid bigint NOT NULL,
    gid bigint NOT NULL
);


ALTER TABLE public.facebook_users_groups OWNER TO jmsc;

--
-- Name: facebook_applications_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY facebook_applications
    ADD CONSTRAINT facebook_applications_pkey PRIMARY KEY (id);


--
-- Name: facebook_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY facebook_comments
    ADD CONSTRAINT facebook_comments_pkey PRIMARY KEY (id);


--
-- Name: facebook_events_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY facebook_events
    ADD CONSTRAINT facebook_events_pkey PRIMARY KEY (id);


--
-- Name: facebook_events_watch_id; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY facebook_events_watch
    ADD CONSTRAINT facebook_events_watch_id PRIMARY KEY (eid, retrieved);


--
-- Name: facebook_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY facebook_groups
    ADD CONSTRAINT facebook_groups_pkey PRIMARY KEY (id);


--
-- Name: facebook_groups_watch_id; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY facebook_groups_watch
    ADD CONSTRAINT facebook_groups_watch_id PRIMARY KEY (gid, retrieved);


--
-- Name: facebook_likes_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY facebook_likes
    ADD CONSTRAINT facebook_likes_pkey PRIMARY KEY (uid, pid);


--
-- Name: facebook_mylists_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY facebook_mylists
    ADD CONSTRAINT facebook_mylists_pkey PRIMARY KEY (id);


--
-- Name: facebook_pages_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY facebook_pages
    ADD CONSTRAINT facebook_pages_pkey PRIMARY KEY (id);


--
-- Name: facebook_posts_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY facebook_posts
    ADD CONSTRAINT facebook_posts_pkey PRIMARY KEY (id);


--
-- Name: facebook_userlist_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY facebook_userlist
    ADD CONSTRAINT facebook_userlist_pkey PRIMARY KEY (obj_id, obj_type, list_id);


--
-- Name: facebook_users_events_id; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY facebook_users_events
    ADD CONSTRAINT facebook_users_events_id PRIMARY KEY (uid, eid);


--
-- Name: facebook_users_groups_id; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY facebook_users_groups
    ADD CONSTRAINT facebook_users_groups_id PRIMARY KEY (uid, gid);


--
-- Name: facebook_users_pkey; Type: CONSTRAINT; Schema: public; Owner: jmsc; Tablespace: 
--

ALTER TABLE ONLY facebook_users
    ADD CONSTRAINT facebook_users_pkey PRIMARY KEY (id);


--
-- Name: facebook_comments_from; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE INDEX facebook_comments_from ON facebook_comments USING btree ("from");


--
-- Name: facebook_posts_created_time_idx; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE INDEX facebook_posts_created_time_idx ON facebook_posts USING btree (created_time);


--
-- Name: facebook_posts_from_idx; Type: INDEX; Schema: public; Owner: jmsc; Tablespace: 
--

CREATE INDEX facebook_posts_from_idx ON facebook_posts USING btree ("from");


--
-- Name: facebook_applications; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE facebook_applications FROM PUBLIC;
REVOKE ALL ON TABLE facebook_applications FROM jmsc;
GRANT ALL ON TABLE facebook_applications TO jmsc;
GRANT SELECT ON TABLE facebook_applications TO social_user;


--
-- Name: facebook_events; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE facebook_events FROM PUBLIC;
REVOKE ALL ON TABLE facebook_events FROM jmsc;
GRANT ALL ON TABLE facebook_events TO jmsc;
GRANT SELECT ON TABLE facebook_events TO social_user;


--
-- Name: facebook_events_watch; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE facebook_events_watch FROM PUBLIC;
REVOKE ALL ON TABLE facebook_events_watch FROM jmsc;
GRANT ALL ON TABLE facebook_events_watch TO jmsc;
GRANT SELECT ON TABLE facebook_events_watch TO social_user;


--
-- Name: facebook_groups; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE facebook_groups FROM PUBLIC;
REVOKE ALL ON TABLE facebook_groups FROM jmsc;
GRANT ALL ON TABLE facebook_groups TO jmsc;
GRANT SELECT ON TABLE facebook_groups TO social_user;


--
-- Name: facebook_groups_watch; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE facebook_groups_watch FROM PUBLIC;
REVOKE ALL ON TABLE facebook_groups_watch FROM jmsc;
GRANT ALL ON TABLE facebook_groups_watch TO jmsc;
GRANT SELECT ON TABLE facebook_groups_watch TO social_user;


--
-- Name: facebook_mylists; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE facebook_mylists FROM PUBLIC;
REVOKE ALL ON TABLE facebook_mylists FROM jmsc;
GRANT ALL ON TABLE facebook_mylists TO jmsc;
GRANT SELECT ON TABLE facebook_mylists TO social_user;


--
-- Name: facebook_pages; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE facebook_pages FROM PUBLIC;
REVOKE ALL ON TABLE facebook_pages FROM jmsc;
GRANT ALL ON TABLE facebook_pages TO jmsc;
GRANT SELECT ON TABLE facebook_pages TO social_user;


--
-- Name: facebook_pages_watch; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE facebook_pages_watch FROM PUBLIC;
REVOKE ALL ON TABLE facebook_pages_watch FROM jmsc;
GRANT ALL ON TABLE facebook_pages_watch TO jmsc;
GRANT SELECT ON TABLE facebook_pages_watch TO social_user;


--
-- Name: facebook_posts; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE facebook_posts FROM PUBLIC;
REVOKE ALL ON TABLE facebook_posts FROM jmsc;
GRANT ALL ON TABLE facebook_posts TO jmsc;
GRANT SELECT ON TABLE facebook_posts TO social_user;


--
-- Name: facebook_userlist; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE facebook_userlist FROM PUBLIC;
REVOKE ALL ON TABLE facebook_userlist FROM jmsc;
GRANT ALL ON TABLE facebook_userlist TO jmsc;
GRANT SELECT ON TABLE facebook_userlist TO social_user;


--
-- Name: facebook_users; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE facebook_users FROM PUBLIC;
REVOKE ALL ON TABLE facebook_users FROM jmsc;
GRANT ALL ON TABLE facebook_users TO jmsc;
GRANT SELECT ON TABLE facebook_users TO social_user;


--
-- Name: facebook_users_events; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE facebook_users_events FROM PUBLIC;
REVOKE ALL ON TABLE facebook_users_events FROM jmsc;
GRANT ALL ON TABLE facebook_users_events TO jmsc;
GRANT SELECT ON TABLE facebook_users_events TO social_user;


--
-- Name: facebook_users_groups; Type: ACL; Schema: public; Owner: jmsc
--

REVOKE ALL ON TABLE facebook_users_groups FROM PUBLIC;
REVOKE ALL ON TABLE facebook_users_groups FROM jmsc;
GRANT ALL ON TABLE facebook_users_groups TO jmsc;
GRANT SELECT ON TABLE facebook_users_groups TO social_user;


--
-- PostgreSQL database dump complete
--

