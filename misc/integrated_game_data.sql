/* Create users */
INSERT INTO users
    (first_name, last_name, email, phone_number, birth_date, role, language_id)
VALUES
    ('user', 'name', 'one@email.com', '1111111111', '01/01/2000'::date, 'super-admin', 1),
    ('user', 'name', 'two@email.com', '2222222222', '01/01/2001'::date, 'student', 2),
    ('user', 'name', 'three@email.com', '3333333333', '01/01/2002'::date, 'student', 2),
    ('user', 'name', 'four@email.com', '4444444444', '01/01/2003'::date, 'student', 2),
    ('user', 'name', 'five@email.com', '5555555555', '01/01/2004'::date, 'student', 3),
    ('user', 'name', 'six@email.com', '6666666666', '01/01/2005'::date, 'student', 3),
    ('user', 'name', 'seven@email.com', '7777777777', '01/01/2006'::date, 'student', 3);


/* Create game */
INSERT INTO games
    (created_by, game_type_id, rounds, practice)
VALUES
    (1, 1, 10, FALSE);

/* Add users to game */
INSERT INTO game_players
    (created_by, game_id, user_id, position, name_hidden)
VALUES
    (1, 1, 2, 1, FALSE),
    (1, 1, 3, 2, FALSE),
    (1, 1, 4, 3, FALSE),
    (1, 1, 5, 4, FALSE),
    (1, 1, 6, 3, FALSE),
    (1, 1, 7, 4, FALSE);
