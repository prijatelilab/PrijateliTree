/* Create languages */
INSERT INTO languages
	(id, created_at, name, abbr)
VALUES
	(1, '01/01/2000'::date, 'English', 'en'),
	(2, '01/01/2000'::date, 'Macedonian', 'mk'),
	(3, '01/01/2000'::date, 'Albanian', 'al'),
	(4, '01/01/2000'::date, 'Turkish', 'tr');


/* Create highschools */
INSERT INTO high_schools
    (id, created_at, name)
VALUES
    (1, '01/01/2000'::date, 'school 1'),
    (2, '01/01/2000'::date, 'school 2'),
    (3, '01/01/2000'::date, 'school 3');


/* Create users */
INSERT INTO users
    (id, created_at, created_by, first_name, last_name, email, birth_date, qualtrics_id, role, grade_level, language_id, high_school_id, uuid)
VALUES
    (1, '01/01/2000'::date, 1, 'admin', 'name', 'a@email.com', '01/01/2000'::date, 1, 'super-admin', 1, 1, 1,gen_random_uuid ()),
    (2, '01/01/2000'::date, 1, 'macedonian', 'name', 'b@email.com', '01/01/2001'::date, 1, 'student', 2, 1, 1, gen_random_uuid ()),
    (3, '01/01/2000'::date, 1, 'macedonian', 'name', 'c@email.com', '01/01/2002'::date, 1,  'student', 2, 2, 1, gen_random_uuid ()),
    (4, '01/01/2000'::date, 1, 'macedonian', 'name', 'd@email.com', '01/01/2003'::date, 1, 'student', 2, 3, 2, gen_random_uuid ()),
    (5, '01/01/2000'::date, 1, 'albanian', 'name', 'e@email.com', '01/01/2004'::date, 1, 'student', 3, 1, 2, gen_random_uuid ()),
    (6, '01/01/2000'::date, 1, 'albanian', 'name', 'f@email.com', '01/01/2005'::date, 1, 'student', 3, 2, 2, gen_random_uuid ()),
    (7, '01/01/2000'::date, 1, 'albanian', 'name', 'g@email.com', '01/01/2006'::date, 1, 'student', 3, 3, 3, gen_random_uuid ()),
    (8, '01/01/2000'::date, 1, 'turkish', 'name', 'h@email.com', '01/01/2007'::date, 1, 'student', 4, 1, 3, gen_random_uuid ()),
    (9, '01/01/2000'::date, 1, 'turkish', 'name', 'i@email.com', '01/01/2008'::date, 1, 'student', 4, 2, 3, gen_random_uuid ()),
    (10, '01/01/2000'::date, 1, 'turkish', 'name', 'j@email.com', '01/01/2009'::date, 1, 'student', 4, 3, 3, gen_random_uuid ());

   
/* Create game */
INSERT INTO games
    (created_by, game_type_id, rounds, practice)
VALUES
    (1, 1, 10, FALSE);

/* Add users to game */
INSERT INTO game_players
    (created_by, game_id, user_id, position, name_hidden, ready)
VALUES
    (1, 1, 2, 1, FALSE, FALSE),
    (1, 1, 3, 2, FALSE, FALSE),
    (1, 1, 4, 3, FALSE, FALSE),
    (1, 1, 5, 4, FALSE, FALSE),
    (1, 1, 6, 3, FALSE, FALSE),
    (1, 1, 7, 4, FALSE, FALSE);