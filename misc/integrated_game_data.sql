/* Create languages */
INSERT INTO languages
	(id, created_at, name, abbr)
VALUES
	()


/* Create users */
INSERT INTO users
    (first_name, last_name, email, birth_date, role, language_id, high_school_id)
VALUES
    ('admin', 'name', 'one@email.com', '01/01/2000'::date, 'super-admin', 1, NULL),
    ('macedonian', 'name', 'two@email.com', '01/01/2001'::date, 'student', 2, 1),
    ('macedonian', 'name', 'three@email.com', '01/01/2002'::date, 'student', 2, 2),
    ('macedonian', 'name', 'four@email.com', '01/01/2003'::date, 'student', 2, 3),
    ('albanian', 'name', 'five@email.com', '01/01/2004'::date, 'student', 3, 1),
    ('albanian', 'name', 'six@email.com', '01/01/2005'::date, 'student', 3, 2),
    ('albanian', 'name', 'seven@email.com', '01/01/2006'::date, 'student', 3, 3),
    ('turkish', 'name', 'eight@email.com', '01/01/2007'::date, 'student', 4, 1),
    ('turkish', 'name', 'nine@email.com', '01/01/2008'::date, 'student', 4, 2),
    ('turkish', 'name', 'ten@email.com', '01/01/2009'::date, 'student', 4, 3);


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
