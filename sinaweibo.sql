-- Table: sinaweibo

-- DROP TABLE sinaweibo;

CREATE TABLE sinaweibo
(
 id bigint NOT NULL,
 created_at timestamp without time zone,
 "text" text,
 in_reply_to_user_id bigint,
 in_reply_to_screen_name character varying(25),
 in_reply_to_status_id bigint,
 screen_name character varying(25),
 user_id bigint,
 CONSTRAINT sinaweibo_pkey PRIMARY KEY (id)
 )
WITH (
	OIDS=FALSE
     );
ALTER TABLE sinaweibo OWNER TO YOURUSER;



-- Table: sinaweibo_followers

-- DROP TABLE sinaweibo_followers;

CREATE TABLE sinaweibo_followers
(
 source_id bigint NOT NULL,
 target_id bigint NOT NULL,
 retrieved timestamp without time zone NOT NULL DEFAULT now(),
 CONSTRAINT sinaweibo_followers_pkey PRIMARY KEY (source_id, target_id)
 )
WITH (
	OIDS=FALSE
     );
ALTER TABLE sinaweibo_followers OWNER TO YOUR_USER;

-- Index: sinaweibo_followers_source_target

-- DROP INDEX sinaweibo_followers_source_target;

CREATE UNIQUE INDEX sinaweibo_followers_source_target
ON sinaweibo_followers
USING btree
(source_id, target_id);


-- Table: sinaweibo_friends

-- DROP TABLE sinaweibo_friends;

CREATE TABLE sinaweibo_friends
(
 source_id bigint NOT NULL,
 target_id bigint NOT NULL,
 retrieved timestamp without time zone NOT NULL DEFAULT now(),
 CONSTRAINT sinaweibo_friends_pkey PRIMARY KEY (source_id, target_id)
 )
WITH (
	OIDS=FALSE
     );
ALTER TABLE sinaweibo_friends OWNER TO YOUR_USER;

-- Index: sinaweibo_friends_source_target

-- DROP INDEX sinaweibo_friends_source_target;

CREATE UNIQUE INDEX sinaweibo_friends_source_target
ON sinaweibo_friends
USING btree
(source_id, target_id);


-- Table: sinaweibo_users

-- DROP TABLE sinaweibo_users;

CREATE TABLE sinaweibo_users
(
 retrieved timestamp without time zone,
 id bigint NOT NULL,
 "name" character varying(64),
 screen_name character varying(64) NOT NULL,
 province smallint,
 city smallint,
 "location" character varying(64),
 description character varying(512),
 profile_image_url character varying(256),
 url character varying(256),
 "domain" character varying(256),
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
 CONSTRAINT sinaweibo_users_pkey PRIMARY KEY (id)
    )
    WITH (
	    OIDS=FALSE
	 );
    ALTER TABLE sinaweibo_users OWNER TO YOUR_USER;

