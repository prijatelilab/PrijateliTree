/* Create users */
INSERT INTO users
    (first_name, last_name, email, birth_date, role, grade_level, language_id, high_school_id)
VALUES
    ('admin', 'name', 'a@email.com', '01/01/2000'::date, 'super-admin', 1, 1, 1),
    ('macedonian 1', 'name', 'b@email.com', '01/01/2001'::date, 'student', 2, 2, 1),
    ('macedonian 2', 'name', 'c@email.com', '01/01/2002'::date,  'student', 2, 2, 1),
    ('macedonian 3', 'name', 'd@email.com', '01/01/2003'::date, 'student', 2, 2, 2),
    ('albanian 1', 'name', 'e@email.com', '01/01/2004'::date, 'student', 3, 3, 2),
    ('albanian 2', 'name', 'f@email.com', '01/01/2005'::date, 'student', 3, 3, 2),
    ('albanian 3', 'name', 'g@email.com', '01/01/2006'::date, 'student', 3, 3, 3),
    ('turkish 1', 'name', 'h@email.com', '01/01/2007'::date, 'student', 4, 4, 3),
    ('turkish 2', 'name', 'i@email.com', '01/01/2008'::date, 'student', 4, 4, 3),
    ('turkish 3', 'name', 'j@email.com', '01/01/2009'::date, 'student', 4, 4, 3);


/* Create session */
INSERT INTO sessions
    (id, created_at, created_by, num_games, finished)
VALUES
    (1, '01/01/2000'::date, 1, 1, FALSE);

/* Create game */
INSERT INTO games
    (created_by, game_type_id, rounds, practice)
VALUES
    (1, 1, 10, FALSE);

/* Add users to game */
INSERT INTO game_players
    (created_by, game_id, user_id, position, ready)
VALUES
    (1, 1, 2, 1, FALSE),
    (1, 1, 3, 2, FALSE),
    (1, 1, 4, 3, FALSE),
    (1, 1, 5, 4, FALSE),
    (1, 1, 6, 5, FALSE),
    (1, 1, 7, 6, FALSE);
