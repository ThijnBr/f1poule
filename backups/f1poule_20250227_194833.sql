--
-- PostgreSQL database dump
--

-- Dumped from database version 17rc1
-- Dumped by pg_dump version 17rc1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: bonusprediction; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bonusprediction (
    id integer NOT NULL,
    user_id integer,
    poule integer,
    track integer,
    fastestlap integer,
    dnf integer,
    dod integer,
    flpoints integer,
    dnfpoints integer,
    dodpoints integer
);


--
-- Name: bonusprediction_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bonusprediction_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bonusprediction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bonusprediction_id_seq OWNED BY public.bonusprediction.id;


--
-- Name: bonusresults; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bonusresults (
    id integer NOT NULL,
    fl integer,
    dod integer,
    track integer
);


--
-- Name: bonusresults_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bonusresults_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bonusresults_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bonusresults_id_seq OWNED BY public.bonusresults.id;


--
-- Name: driver; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.driver (
    driver_id integer NOT NULL,
    driver_name character varying(100) NOT NULL,
    driver_team character varying(100) NOT NULL
);


--
-- Name: driver_driver_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.driver_driver_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: driver_driver_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.driver_driver_id_seq OWNED BY public.driver.driver_id;


--
-- Name: headtohead; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.headtohead (
    id integer NOT NULL,
    driver1_id integer,
    driver2_id integer
);


--
-- Name: headtohead_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.headtohead_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: headtohead_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.headtohead_id_seq OWNED BY public.headtohead.id;


--
-- Name: headtoheadprediction; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.headtoheadprediction (
    id integer NOT NULL,
    user_id integer,
    headtohead_id integer,
    driverselected boolean,
    track integer,
    date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    points integer,
    poule integer
);


--
-- Name: headtoheadprediction_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.headtoheadprediction_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: headtoheadprediction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.headtoheadprediction_id_seq OWNED BY public.headtoheadprediction.id;


--
-- Name: poules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.poules (
    poule_id integer NOT NULL,
    poule_name character varying(50) NOT NULL
);


--
-- Name: poules_poule_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.poules_poule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: poules_poule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.poules_poule_id_seq OWNED BY public.poules.poule_id;


--
-- Name: qualiresults; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.qualiresults (
    id integer NOT NULL,
    track_id integer,
    "position" integer,
    driver_id integer,
    result_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    dnf boolean
);


--
-- Name: qualiresults_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.qualiresults_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: qualiresults_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.qualiresults_id_seq OWNED BY public.qualiresults.id;


--
-- Name: raceresults; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.raceresults (
    id integer NOT NULL,
    track_id integer,
    "position" integer,
    driver_id integer,
    dnf boolean,
    result_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: raceresults_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.raceresults_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: raceresults_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.raceresults_id_seq OWNED BY public.raceresults.id;


--
-- Name: top3_quali; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.top3_quali (
    id integer NOT NULL,
    user_id integer,
    driver1_id integer,
    driver2_id integer,
    driver3_id integer,
    driver1points integer DEFAULT 0,
    driver2points integer DEFAULT 0,
    driver3points integer DEFAULT 0,
    track integer,
    date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    poule integer
);


--
-- Name: top3_quali_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.top3_quali_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: top3_quali_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.top3_quali_id_seq OWNED BY public.top3_quali.id;


--
-- Name: top5_race; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.top5_race (
    id integer NOT NULL,
    user_id integer,
    driver1_id integer,
    driver2_id integer,
    driver3_id integer,
    driver4_id integer,
    driver5_id integer,
    driver1points integer DEFAULT 0,
    driver2points integer DEFAULT 0,
    driver3points integer DEFAULT 0,
    driver4points integer DEFAULT 0,
    driver5points integer DEFAULT 0,
    track integer,
    date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    poule integer
);


--
-- Name: top5_race_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.top5_race_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: top5_race_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.top5_race_id_seq OWNED BY public.top5_race.id;


--
-- Name: track; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.track (
    id integer NOT NULL,
    track_name character varying(50),
    track_quali_date timestamp without time zone,
    track_race_date timestamp without time zone
);


--
-- Name: track_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.track_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: track_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.track_id_seq OWNED BY public.track.id;


--
-- Name: user_poule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_poule (
    user_id integer NOT NULL,
    poule_id integer NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    username character varying(50) NOT NULL,
    password character varying(100) NOT NULL
);


--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: bonusprediction id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bonusprediction ALTER COLUMN id SET DEFAULT nextval('public.bonusprediction_id_seq'::regclass);


--
-- Name: bonusresults id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bonusresults ALTER COLUMN id SET DEFAULT nextval('public.bonusresults_id_seq'::regclass);


--
-- Name: driver driver_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.driver ALTER COLUMN driver_id SET DEFAULT nextval('public.driver_driver_id_seq'::regclass);


--
-- Name: headtohead id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.headtohead ALTER COLUMN id SET DEFAULT nextval('public.headtohead_id_seq'::regclass);


--
-- Name: headtoheadprediction id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.headtoheadprediction ALTER COLUMN id SET DEFAULT nextval('public.headtoheadprediction_id_seq'::regclass);


--
-- Name: poules poule_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.poules ALTER COLUMN poule_id SET DEFAULT nextval('public.poules_poule_id_seq'::regclass);


--
-- Name: qualiresults id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.qualiresults ALTER COLUMN id SET DEFAULT nextval('public.qualiresults_id_seq'::regclass);


--
-- Name: raceresults id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.raceresults ALTER COLUMN id SET DEFAULT nextval('public.raceresults_id_seq'::regclass);


--
-- Name: top3_quali id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top3_quali ALTER COLUMN id SET DEFAULT nextval('public.top3_quali_id_seq'::regclass);


--
-- Name: top5_race id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top5_race ALTER COLUMN id SET DEFAULT nextval('public.top5_race_id_seq'::regclass);


--
-- Name: track id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.track ALTER COLUMN id SET DEFAULT nextval('public.track_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: bonusprediction; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.bonusprediction (id, user_id, poule, track, fastestlap, dnf, dod, flpoints, dnfpoints, dodpoints) FROM stdin;
\.


--
-- Data for Name: bonusresults; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.bonusresults (id, fl, dod, track) FROM stdin;
\.


--
-- Data for Name: driver; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.driver (driver_id, driver_name, driver_team) FROM stdin;
\.


--
-- Data for Name: headtohead; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.headtohead (id, driver1_id, driver2_id) FROM stdin;
\.


--
-- Data for Name: headtoheadprediction; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.headtoheadprediction (id, user_id, headtohead_id, driverselected, track, date, points, poule) FROM stdin;
\.


--
-- Data for Name: poules; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.poules (poule_id, poule_name) FROM stdin;
\.


--
-- Data for Name: qualiresults; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.qualiresults (id, track_id, "position", driver_id, result_date, dnf) FROM stdin;
\.


--
-- Data for Name: raceresults; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.raceresults (id, track_id, "position", driver_id, dnf, result_date) FROM stdin;
\.


--
-- Data for Name: top3_quali; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.top3_quali (id, user_id, driver1_id, driver2_id, driver3_id, driver1points, driver2points, driver3points, track, date, poule) FROM stdin;
\.


--
-- Data for Name: top5_race; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.top5_race (id, user_id, driver1_id, driver2_id, driver3_id, driver4_id, driver5_id, driver1points, driver2points, driver3points, driver4points, driver5points, track, date, poule) FROM stdin;
\.


--
-- Data for Name: track; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.track (id, track_name, track_quali_date, track_race_date) FROM stdin;
\.


--
-- Data for Name: user_poule; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_poule (user_id, poule_id) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (user_id, username, password) FROM stdin;
\.


--
-- Name: bonusprediction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.bonusprediction_id_seq', 1, false);


--
-- Name: bonusresults_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.bonusresults_id_seq', 1, false);


--
-- Name: driver_driver_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.driver_driver_id_seq', 1, false);


--
-- Name: headtohead_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.headtohead_id_seq', 1, false);


--
-- Name: headtoheadprediction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.headtoheadprediction_id_seq', 1, false);


--
-- Name: poules_poule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.poules_poule_id_seq', 1, false);


--
-- Name: qualiresults_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.qualiresults_id_seq', 1, false);


--
-- Name: raceresults_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.raceresults_id_seq', 1, false);


--
-- Name: top3_quali_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.top3_quali_id_seq', 1, false);


--
-- Name: top5_race_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.top5_race_id_seq', 1, false);


--
-- Name: track_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.track_id_seq', 1, false);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_user_id_seq', 1, false);


--
-- Name: bonusprediction bonusprediction_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bonusprediction
    ADD CONSTRAINT bonusprediction_pkey PRIMARY KEY (id);


--
-- Name: bonusresults bonusresults_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bonusresults
    ADD CONSTRAINT bonusresults_pkey PRIMARY KEY (id);


--
-- Name: bonusresults bonusresults_track_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bonusresults
    ADD CONSTRAINT bonusresults_track_key UNIQUE (track);


--
-- Name: driver driver_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.driver
    ADD CONSTRAINT driver_pkey PRIMARY KEY (driver_id);


--
-- Name: headtohead headtohead_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.headtohead
    ADD CONSTRAINT headtohead_pkey PRIMARY KEY (id);


--
-- Name: headtoheadprediction headtoheadprediction_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.headtoheadprediction
    ADD CONSTRAINT headtoheadprediction_pkey PRIMARY KEY (id);


--
-- Name: poules poules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.poules
    ADD CONSTRAINT poules_pkey PRIMARY KEY (poule_id);


--
-- Name: qualiresults qualiresults_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.qualiresults
    ADD CONSTRAINT qualiresults_pkey PRIMARY KEY (id);


--
-- Name: raceresults raceresults_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.raceresults
    ADD CONSTRAINT raceresults_pkey PRIMARY KEY (id);


--
-- Name: top3_quali top3_quali_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top3_quali
    ADD CONSTRAINT top3_quali_pkey PRIMARY KEY (id);


--
-- Name: top5_race top5_race_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top5_race
    ADD CONSTRAINT top5_race_pkey PRIMARY KEY (id);


--
-- Name: track track_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.track
    ADD CONSTRAINT track_pkey PRIMARY KEY (id);


--
-- Name: user_poule unique_user_poule; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_poule
    ADD CONSTRAINT unique_user_poule PRIMARY KEY (user_id, poule_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: bonusprediction bonusprediction_dnf_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bonusprediction
    ADD CONSTRAINT bonusprediction_dnf_fkey FOREIGN KEY (dnf) REFERENCES public.driver(driver_id);


--
-- Name: bonusprediction bonusprediction_dod_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bonusprediction
    ADD CONSTRAINT bonusprediction_dod_fkey FOREIGN KEY (dod) REFERENCES public.driver(driver_id);


--
-- Name: bonusprediction bonusprediction_fastestlap_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bonusprediction
    ADD CONSTRAINT bonusprediction_fastestlap_fkey FOREIGN KEY (fastestlap) REFERENCES public.driver(driver_id);


--
-- Name: bonusprediction bonusprediction_poule_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bonusprediction
    ADD CONSTRAINT bonusprediction_poule_fkey FOREIGN KEY (poule) REFERENCES public.poules(poule_id);


--
-- Name: bonusprediction bonusprediction_track_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bonusprediction
    ADD CONSTRAINT bonusprediction_track_fkey FOREIGN KEY (track) REFERENCES public.track(id);


--
-- Name: bonusprediction bonusprediction_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bonusprediction
    ADD CONSTRAINT bonusprediction_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: bonusresults bonusresults_dod_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bonusresults
    ADD CONSTRAINT bonusresults_dod_fkey FOREIGN KEY (dod) REFERENCES public.driver(driver_id);


--
-- Name: bonusresults bonusresults_fl_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bonusresults
    ADD CONSTRAINT bonusresults_fl_fkey FOREIGN KEY (fl) REFERENCES public.driver(driver_id);


--
-- Name: bonusresults bonusresults_track_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bonusresults
    ADD CONSTRAINT bonusresults_track_fkey FOREIGN KEY (track) REFERENCES public.track(id);


--
-- Name: headtohead headtohead_driver1_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.headtohead
    ADD CONSTRAINT headtohead_driver1_id_fkey FOREIGN KEY (driver1_id) REFERENCES public.driver(driver_id);


--
-- Name: headtohead headtohead_driver2_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.headtohead
    ADD CONSTRAINT headtohead_driver2_id_fkey FOREIGN KEY (driver2_id) REFERENCES public.driver(driver_id);


--
-- Name: headtoheadprediction headtoheadprediction_headtohead_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.headtoheadprediction
    ADD CONSTRAINT headtoheadprediction_headtohead_id_fkey FOREIGN KEY (headtohead_id) REFERENCES public.headtohead(id);


--
-- Name: headtoheadprediction headtoheadprediction_poule_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.headtoheadprediction
    ADD CONSTRAINT headtoheadprediction_poule_fkey FOREIGN KEY (poule) REFERENCES public.poules(poule_id);


--
-- Name: headtoheadprediction headtoheadprediction_track_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.headtoheadprediction
    ADD CONSTRAINT headtoheadprediction_track_fkey FOREIGN KEY (track) REFERENCES public.track(id);


--
-- Name: headtoheadprediction headtoheadprediction_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.headtoheadprediction
    ADD CONSTRAINT headtoheadprediction_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: qualiresults qualiresults_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.qualiresults
    ADD CONSTRAINT qualiresults_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.driver(driver_id);


--
-- Name: qualiresults qualiresults_track_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.qualiresults
    ADD CONSTRAINT qualiresults_track_id_fkey FOREIGN KEY (track_id) REFERENCES public.track(id);


--
-- Name: raceresults raceresults_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.raceresults
    ADD CONSTRAINT raceresults_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.driver(driver_id);


--
-- Name: raceresults raceresults_track_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.raceresults
    ADD CONSTRAINT raceresults_track_id_fkey FOREIGN KEY (track_id) REFERENCES public.track(id);


--
-- Name: top3_quali top3_quali_driver1_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top3_quali
    ADD CONSTRAINT top3_quali_driver1_id_fkey FOREIGN KEY (driver1_id) REFERENCES public.driver(driver_id);


--
-- Name: top3_quali top3_quali_driver2_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top3_quali
    ADD CONSTRAINT top3_quali_driver2_id_fkey FOREIGN KEY (driver2_id) REFERENCES public.driver(driver_id);


--
-- Name: top3_quali top3_quali_driver3_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top3_quali
    ADD CONSTRAINT top3_quali_driver3_id_fkey FOREIGN KEY (driver3_id) REFERENCES public.driver(driver_id);


--
-- Name: top3_quali top3_quali_poule_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top3_quali
    ADD CONSTRAINT top3_quali_poule_fkey FOREIGN KEY (poule) REFERENCES public.poules(poule_id);


--
-- Name: top3_quali top3_quali_track_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top3_quali
    ADD CONSTRAINT top3_quali_track_fkey FOREIGN KEY (track) REFERENCES public.track(id);


--
-- Name: top3_quali top3_quali_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top3_quali
    ADD CONSTRAINT top3_quali_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: top5_race top5_race_driver1_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top5_race
    ADD CONSTRAINT top5_race_driver1_id_fkey FOREIGN KEY (driver1_id) REFERENCES public.driver(driver_id);


--
-- Name: top5_race top5_race_driver2_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top5_race
    ADD CONSTRAINT top5_race_driver2_id_fkey FOREIGN KEY (driver2_id) REFERENCES public.driver(driver_id);


--
-- Name: top5_race top5_race_driver3_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top5_race
    ADD CONSTRAINT top5_race_driver3_id_fkey FOREIGN KEY (driver3_id) REFERENCES public.driver(driver_id);


--
-- Name: top5_race top5_race_driver4_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top5_race
    ADD CONSTRAINT top5_race_driver4_id_fkey FOREIGN KEY (driver4_id) REFERENCES public.driver(driver_id);


--
-- Name: top5_race top5_race_driver5_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top5_race
    ADD CONSTRAINT top5_race_driver5_id_fkey FOREIGN KEY (driver5_id) REFERENCES public.driver(driver_id);


--
-- Name: top5_race top5_race_poule_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top5_race
    ADD CONSTRAINT top5_race_poule_fkey FOREIGN KEY (poule) REFERENCES public.poules(poule_id);


--
-- Name: top5_race top5_race_track_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top5_race
    ADD CONSTRAINT top5_race_track_fkey FOREIGN KEY (track) REFERENCES public.track(id);


--
-- Name: top5_race top5_race_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.top5_race
    ADD CONSTRAINT top5_race_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: user_poule user_poule_poule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_poule
    ADD CONSTRAINT user_poule_poule_id_fkey FOREIGN KEY (poule_id) REFERENCES public.poules(poule_id) ON DELETE CASCADE;


--
-- Name: user_poule user_poule_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_poule
    ADD CONSTRAINT user_poule_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

