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
INSERT INTO game_sessions
    (id, created_at, created_by, num_games, finished)
VALUES
    (1, '01/01/2000'::date, 1, 1, FALSE);

/* Create game */
INSERT INTO games
    (created_by, game_type_id, rounds, practice, game_session_id)
VALUES
    (1, 1, 2, TRUE, 1),
    (1, 1, 10, FALSE, 1);

/* Create Session Players */
INSERT INTO session_players
    (id, created_at, created_by, user_id, session_id, ready, points, correct_answers)
VALUES
    (1, '01/01/2000'::date, 1, 2, 1, FALSE, 0, 0),
    (2, '01/01/2000'::date, 1, 3, 1, FALSE, 0, 0),
    (3, '01/01/2000'::date, 1, 4, 1, FALSE, 0, 0),
    (4, '01/01/2000'::date, 1, 5, 1, FALSE, 0, 0),
    (5, '01/01/2000'::date, 1, 6, 1, FALSE, 0, 0),
    (6, '01/01/2000'::date, 1, 7, 1, FALSE, 0, 0);


/* Add users to game */
INSERT INTO game_players
    (created_by, game_id, user_id, position, ready, session_player_id, initial_ball)
VALUES
    (1, 1, 2, 1, false, 1, 'R'),
    (1, 1, 3, 2, false, 1, 'B'),
    (1, 1, 4, 3, false, 1, 'B'),
    (1, 1, 5, 4, false, 1, 'R'),
    (1, 1, 6, 5, false, 1, 'R'),
    (1, 1, 7, 6, false, 1, 'B'),
    (1, 2, 2, 1, false, 1, 'R'),
    (1, 2, 3, 2, false, 1, 'B'),
    (1, 2, 4, 3, false, 1, 'R'),
    (1, 2, 5, 4, false, 1, 'B'),
    (1, 2, 6, 5, false, 1, 'R'),
    (1, 2, 7, 6, false, 1, 'B');
