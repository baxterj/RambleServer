CREATE TABLE rambleon_authlinkcode
(
  id serial NOT NULL,
  user_id integer NOT NULL,
  code character varying(40) NOT NULL,
  CONSTRAINT rambleon_authlinkcode_pkey PRIMARY KEY (id),
  CONSTRAINT rambleon_authlinkcode_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES rambleon_user (id) MATCH SIMPLE
);

CREATE TABLE rambleon_doneit
(
  id serial NOT NULL,
  user_id integer NOT NULL,
  route_id integer NOT NULL,
  date timestamp with time zone NOT NULL,
  CONSTRAINT rambleon_doneit_pkey PRIMARY KEY (id),
  CONSTRAINT rambleon_doneit_route_id_fkey FOREIGN KEY (route_id)
      REFERENCES rambleon_route (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT rambleon_doneit_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES rambleon_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE rambleon_favourite
(
  id serial NOT NULL,
  user_id integer NOT NULL,
  route_id integer NOT NULL,
  date timestamp with time zone NOT NULL,
  CONSTRAINT rambleon_favourite_pkey PRIMARY KEY (id),
  CONSTRAINT rambleon_favourite_route_id_fkey FOREIGN KEY (route_id)
      REFERENCES rambleon_route (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT rambleon_favourite_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES rambleon_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE rambleon_haskeyword
(
  id serial NOT NULL,
  keyword_id integer NOT NULL,
  route_id integer NOT NULL,
  CONSTRAINT rambleon_haskeyword_pkey PRIMARY KEY (id),
  CONSTRAINT rambleon_haskeyword_keyword_id_fkey FOREIGN KEY (keyword_id)
      REFERENCES rambleon_keyword (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT rambleon_haskeyword_route_id_fkey FOREIGN KEY (route_id)
      REFERENCES rambleon_route (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE rambleon_image
(
  id serial NOT NULL,
  user_id integer NOT NULL,
  title character varying(60) NOT NULL,
  image text NOT NULL,
  thumbnail text NOT NULL,
  text text NOT NULL,
  "creationDate" timestamp with time zone NOT NULL,
  "updateDate" timestamp with time zone NOT NULL,
  lat numeric(10,6) NOT NULL,
  lng numeric(10,6) NOT NULL,
  private boolean NOT NULL,
  CONSTRAINT rambleon_image_pkey PRIMARY KEY (id),
  CONSTRAINT rambleon_image_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES rambleon_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE rambleon_keyword
(
  id serial NOT NULL,
  keyword character varying(30) NOT NULL,
  CONSTRAINT rambleon_keyword_pkey PRIMARY KEY (id)
);

CREATE TABLE rambleon_note
(
  id serial NOT NULL,
  user_id integer NOT NULL,
  title character varying(60) NOT NULL,
  content text NOT NULL,
  "creationDate" timestamp with time zone NOT NULL,
  "updateDate" timestamp with time zone NOT NULL,
  lat numeric(10,6) NOT NULL,
  lng numeric(10,6) NOT NULL,
  private boolean NOT NULL,
  CONSTRAINT rambleon_note_pkey PRIMARY KEY (id),
  CONSTRAINT rambleon_note_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES rambleon_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE rambleon_pathpoint
(
  id serial NOT NULL,
  route_id integer NOT NULL,
  "orderNum" integer NOT NULL,
  lat numeric(10,6) NOT NULL,
  lng numeric(10,6) NOT NULL,
  CONSTRAINT rambleon_pathpoint_pkey PRIMARY KEY (id),
  CONSTRAINT rambleon_pathpoint_route_id_fkey FOREIGN KEY (route_id)
      REFERENCES rambleon_route (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE rambleon_route
(
  id serial NOT NULL,
  user_id integer NOT NULL,
  name character varying(200) NOT NULL,
  creation_date timestamp with time zone NOT NULL,
  update_date timestamp with time zone NOT NULL,
  private boolean NOT NULL,
  "mapThumbnail" text NOT NULL,
  CONSTRAINT rambleon_route_pkey PRIMARY KEY (id),
  CONSTRAINT rambleon_route_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES rambleon_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE rambleon_speedtrackdata
(
  id serial NOT NULL,
  user_id integer NOT NULL,
  "dateRecorded" timestamp with time zone NOT NULL,
  speed numeric(6,2) NOT NULL,
  altitude numeric(6,2) NOT NULL,
  CONSTRAINT rambleon_speedtrackdata_pkey PRIMARY KEY (id),
  CONSTRAINT rambleon_speedtrackdata_user_id_fkey FOREIGN KEY (user_id)
      REFERENCES rambleon_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE rambleon_user
(
  id serial NOT NULL,
  username character varying(20) NOT NULL,
  email character varying(254) NOT NULL,
  "pwHash" character varying(40) NOT NULL,
  "regDate" timestamp with time zone NOT NULL,
  "lastLogin" timestamp with time zone NOT NULL,
  CONSTRAINT rambleon_user_pkey PRIMARY KEY (id)
);