-- Table: facebook_users

-- DROP TABLE facebook_users;

CREATE TABLE facebook_users
(
  id bigint NOT NULL,
  "name" character varying(256),
  retrieved timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT facebook_users_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE facebook_users OWNER TO jmsc;


-- Table: facebook_users_groups

-- DROP TABLE facebook_users_groups;

CREATE TABLE facebook_users_groups
(
  uid bigint NOT NULL,
  gid bigint NOT NULL,
  CONSTRAINT facebook_users_groups_id PRIMARY KEY (uid, gid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE facebook_users_groups OWNER TO jmsc;
