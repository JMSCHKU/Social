-- Tables that keep the data pulled from Twitter using the twitter.oauth.py script

-- Table: tweets

-- DROP TABLE tweets;

CREATE TABLE tweets
(
  id bigint NOT NULL,
  created_at timestamp without time zone,
  "text" text,
  in_reply_to_user_id bigint,
  in_reply_to_screen_name character varying(25),
  in_reply_to_status_id bigint,
  screen_name character varying(25),
  user_id bigint,
  CONSTRAINT tweets_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE tweets OWNER TO jmsc;


-- Table: twitter_users

-- DROP TABLE twitter_users;

CREATE TABLE twitter_users
(
  id integer NOT NULL DEFAULT nextval('twitter_users_myid_seq'::regclass),
  retrieved timestamp without time zone,
  user_id bigint NOT NULL,
  "name" character varying(32),
  screen_name character varying(32) NOT NULL,
  description character varying(512),
  profile_image_url character varying(256),
  url character varying(256),
  protected boolean,
  followers_count integer,
  friends_count integer,
  created_at timestamp without time zone,
  favourites_count integer,
  utc_offset integer,
  time_zone character varying(128),
  profile_background_image_url character varying(256),
  profile_use_background_image boolean,
  notifications boolean,
  geo_enabled boolean,
  verified boolean,
  following integer,
  statuses_count integer,
  lang character varying(8),
  contributors_enabled boolean,
  follow_request_sent boolean,
  listed_count integer,
  show_all_inline_media boolean,
  CONSTRAINT twitter_users_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE twitter_users OWNER TO jmsc;

