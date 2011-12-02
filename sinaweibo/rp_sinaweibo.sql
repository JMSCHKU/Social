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
    mlevel smallint
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

