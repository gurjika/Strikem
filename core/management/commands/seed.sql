INSERT INTO poolhub.core_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (19, 'pbkdf2_sha256$870000$yhCSRVKnZ14YGGY0vH2Kod$+setkHsx/Se+NX1f4bVW//1hUoeX6jV0FWv1eVPmgQU=', '2024-10-18 15:21:47.095116', 1, 'gurjika', 'luka', 'gurjidze', 'lgurjidze@gmail.com', 1, 1, '2024-09-27 08:51:20.270656');
INSERT INTO poolhub.core_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (39, 'pbkdf2_sha256$870000$siLWyc3S2EiXAeFzOu9JOB$QL631PAAwDGcSwJIY/Z2RjUV/yGqv7HDLvgCflVtX14=', '2024-10-25 16:39:01.153943', 0, 'gendalf', 'Gendalf', 'The Gray', 'gendalf@gmail.com', 0, 1, '2024-10-25 13:37:40.142209');
INSERT INTO poolhub.core_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (40, 'pbkdf2_sha256$870000$wkT1J55rxUZV4F97O1XSuX$9zm5wDWjTA1E9R75CEDissKCCXfPpL0p67UmAKlFjdY=', null, 0, 'butcher', 'Billy', 'Butcher', 'butcher@gmail.com', 0, 1, '2024-10-25 14:08:57.737986');
INSERT INTO poolhub.core_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (42, 'pbkdf2_sha256$870000$68KcGfQYnd0WXZUfLyiMD9$BKVr7QqT7No9bSmxFFBsTRt/lLgg/UNjiVQs2Zzsvj4=', '2024-10-25 22:12:39.846573', 0, 'metropool', 'Metropool', '', 'metropool@gmail.com', 1, 1, '2024-10-25 22:11:20.000000');
INSERT INTO poolhub.poolstore_player (id, games_played, opponents_met, games_won, inviting_to_play, profile_image, total_points, user_id) VALUES (11, 13, 5, 10, 1, 'default.jpg', 1202, 19);
INSERT INTO poolhub.poolstore_player (id, games_played, opponents_met, games_won, inviting_to_play, profile_image, total_points, user_id) VALUES (31, 12, 9, 11, 0, 'profile-pics/gendalf.jpg', 1242, 39);
INSERT INTO poolhub.poolstore_player (id, games_played, opponents_met, games_won, inviting_to_play, profile_image, total_points, user_id) VALUES (32, 5, 5, 2, 0, 'profile-pics/Billy_Butcher.jpg', 1080, 40);
INSERT INTO poolhub.poolstore_player (id, games_played, opponents_met, games_won, inviting_to_play, profile_image, total_points, user_id) VALUES (33, 0, 0, 0, 0, 'default.jpg', 1000, 42);
INSERT INTO poolhub.poolstore_poolhouse (id, title, address, slug, latitude, longitude) VALUES (7, 'Billiard Club Rio', '45 Vazha Pshavela Ave, Tbilisi', 'billiard-club-rio', 41.725889136938555, 44.74357787680199);
INSERT INTO poolhub.poolstore_poolhouse (id, title, address, slug, latitude, longitude) VALUES (8, 'Metropool', '2 floor, Chess Palace, 37a Merab Kostava St, Tbilisi 0179', 'metropool', 41.70846728551126, 44.78757371300003);
INSERT INTO poolhub.poolstore_poolhouse (id, title, address, slug, latitude, longitude) VALUES (9, 'Uni4verse', '77 Giorgi Saakadze Square, Tbilisi', 'uni4verse', 41.72472503851072, 44.77697575901936);
INSERT INTO poolhub.poolstore_poolhouse (id, title, address, slug, latitude, longitude) VALUES (10, 'Ten Ball Billiardvsd', '36g, Moscow Ave, Tbilisi 0137', 'ten-ball-billiardvsd', 41.67550125237992, 44.87777887889215);
INSERT INTO poolhub.poolstore_poolhousestaff (id, poolhouse_id, user_id) VALUES (2, 8, 42);
INSERT INTO poolhub.poolstore_pooltable (id, poolhouse_id, table_id) VALUES (2, 7, 1);
INSERT INTO poolhub.poolstore_pooltable (id, poolhouse_id, table_id) VALUES (3, 7, 2);
INSERT INTO poolhub.poolstore_pooltable (id, poolhouse_id, table_id) VALUES (4, 7, 3);
INSERT INTO poolhub.poolstore_pooltable (id, poolhouse_id, table_id) VALUES (5, 7, 4);
INSERT INTO poolhub.poolstore_pooltable (id, poolhouse_id, table_id) VALUES (6, 8, 1);
INSERT INTO poolhub.poolstore_pooltable (id, poolhouse_id, table_id) VALUES (7, 8, 2);
INSERT INTO poolhub.poolstore_pooltable (id, poolhouse_id, table_id) VALUES (8, 8, 5);
INSERT INTO poolhub.poolstore_pooltable (id, poolhouse_id, table_id) VALUES (9, 9, 1);
INSERT INTO poolhub.poolstore_pooltable (id, poolhouse_id, table_id) VALUES (10, 9, 2);
INSERT INTO poolhub.poolstore_pooltable (id, poolhouse_id, table_id) VALUES (11, 9, 6);
INSERT INTO poolhub.poolstore_pooltable (id, poolhouse_id, table_id) VALUES (12, 9, 5);
INSERT INTO poolhub.poolstore_pooltable (id, poolhouse_id, table_id) VALUES (13, 10, 1);
INSERT INTO poolhub.poolstore_pooltable (id, poolhouse_id, table_id) VALUES (14, 10, 3);
INSERT INTO poolhub.poolstore_pooltable (id, poolhouse_id, table_id) VALUES (15, 10, 5);
INSERT INTO poolhub.poolstore_reservation (id, start_time, duration, end_time, real_end_datetime, player_reserving_id, table_id, finished_reservation, other_player_id) VALUES (7, '2024-10-25 18:00:00.000000', 30, '2024-10-25 18:30:00.000000', '2024-10-25 18:35:00.000000', 32, 2, 0, 31);
INSERT INTO poolhub.poolstore_reservation (id, start_time, duration, end_time, real_end_datetime, player_reserving_id, table_id, finished_reservation, other_player_id) VALUES (9, '2024-10-26 18:19:00.000000', 50, '2024-10-26 19:09:00.000000', '2024-10-26 19:14:00.000000', 31, 2, 0, 11);
INSERT INTO poolhub.poolstore_reservation (id, start_time, duration, end_time, real_end_datetime, player_reserving_id, table_id, finished_reservation, other_player_id) VALUES (10, '2024-10-25 14:50:00.000000', 50, '2024-10-25 15:40:00.000000', '2024-10-25 15:45:00.000000', 11, 2, 0, 32);
INSERT INTO poolhub.poolstore_reservation (id, start_time, duration, end_time, real_end_datetime, player_reserving_id, table_id, finished_reservation, other_player_id) VALUES (20, '2024-10-25 17:02:00.000000', 2, '2024-10-25 17:04:00.000000', '2024-10-25 17:09:00.000000', 11, 9, 1, 31);
INSERT INTO poolhub.poolstore_reservation (id, start_time, duration, end_time, real_end_datetime, player_reserving_id, table_id, finished_reservation, other_player_id) VALUES (21, '2024-10-25 17:06:00.000000', 2, '2024-10-25 17:08:00.000000', '2024-10-25 17:13:00.000000', 11, 9, 1, 31);
INSERT INTO poolhub.poolstore_reservation (id, start_time, duration, end_time, real_end_datetime, player_reserving_id, table_id, finished_reservation, other_player_id) VALUES (22, '2024-10-25 18:14:00.000000', 5, '2024-10-25 18:19:00.000000', '2024-10-25 18:24:00.000000', 11, 5, 1, 32);
INSERT INTO poolhub.poolstore_reservation (id, start_time, duration, end_time, real_end_datetime, player_reserving_id, table_id, finished_reservation, other_player_id) VALUES (24, '2024-10-25 18:31:00.000000', 3, '2024-10-25 18:34:00.000000', '2024-10-25 18:39:00.000000', 11, 5, 1, 31);
INSERT INTO poolhub.poolstore_reservation (id, start_time, duration, end_time, real_end_datetime, player_reserving_id, table_id, finished_reservation, other_player_id) VALUES (25, '2024-10-25 18:36:00.000000', 5, '2024-10-25 18:41:00.000000', '2024-10-25 18:46:00.000000', 11, 5, 1, 32);
INSERT INTO poolhub.poolstore_reservation (id, start_time, duration, end_time, real_end_datetime, player_reserving_id, table_id, finished_reservation, other_player_id) VALUES (26, '2024-10-25 18:53:00.000000', 3, '2024-10-25 18:56:00.000000', '2024-10-25 19:01:00.000000', 11, 5, 1, 32);
INSERT INTO poolhub.poolstore_poolhouserating (id, rate, poolhouse_id, rater_id, review, timestamp) VALUES (1, 4, 7, 11, 'Cozy Place!', '2024-10-25 13:30:46.733000');
INSERT INTO poolhub.poolstore_poolhouserating (id, rate, poolhouse_id, rater_id, review, timestamp) VALUES (2, 5, 7, 31, 'Great Tables.', '2024-10-26 11:33:46.733000');
INSERT INTO poolhub.poolstore_poolhouserating (id, rate, poolhouse_id, rater_id, review, timestamp) VALUES (3, 3, 7, 32, 'Not the best service', '2024-10-26 17:42:46.733000');
INSERT INTO poolhub.poolstore_poolhouserating (id, rate, poolhouse_id, rater_id, review, timestamp) VALUES (4, 4, 8, 11, 'Would come back again.', '2024-10-26 11:42:46.733000');
INSERT INTO poolhub.poolstore_poolhouserating (id, rate, poolhouse_id, rater_id, review, timestamp) VALUES (5, 3, 8, 31, '', '2024-10-13 05:52:46.733000');
INSERT INTO poolhub.poolstore_poolhouserating (id, rate, poolhouse_id, rater_id, review, timestamp) VALUES (6, 2, 8, 32, 'Tables are too close to each other.', '2024-10-22 16:42:46.733000');
INSERT INTO poolhub.poolstore_poolhouserating (id, rate, poolhouse_id, rater_id, review, timestamp) VALUES (7, 5, 9, 11, 'just great', '2024-10-12 21:12:46.733000');
INSERT INTO poolhub.poolstore_poolhouserating (id, rate, poolhouse_id, rater_id, review, timestamp) VALUES (9, 2, 9, 31, 'Our table was in an awful shape.', '2024-10-20 14:30:46.733000');
INSERT INTO poolhub.poolstore_poolhouserating (id, rate, poolhouse_id, rater_id, review, timestamp) VALUES (10, 4, 9, 32, 'good background music and good atmosphere', '2024-10-11 05:32:46.733000');
INSERT INTO poolhub.poolstore_poolhouserating (id, rate, poolhouse_id, rater_id, review, timestamp) VALUES (11, 3, 10, 11, 'cue sticks were not in good shape', '2024-10-25 11:42:46.733000');
INSERT INTO poolhub.poolstore_poolhouserating (id, rate, poolhouse_id, rater_id, review, timestamp) VALUES (12, 4, 10, 31, '', '2024-10-26 07:47:46.733000');
INSERT INTO poolhub.poolstore_poolhouserating (id, rate, poolhouse_id, rater_id, review, timestamp) VALUES (13, 2, 10, 32, 'tables were awful.', '2024-10-23 13:24:46.733000');
INSERT INTO poolhub.poolstore_poolhouseimage (id, image, poolhouse_id) VALUES (16, 'poolhall-pics/rio-2.jpg', 7);
INSERT INTO poolhub.poolstore_poolhouseimage (id, image, poolhouse_id) VALUES (17, 'poolhall-pics/rio-3.jpg', 7);
INSERT INTO poolhub.poolstore_poolhouseimage (id, image, poolhouse_id) VALUES (18, 'poolhall-pics/rio04.jpg', 7);
INSERT INTO poolhub.poolstore_poolhouseimage (id, image, poolhouse_id) VALUES (19, 'poolhall-pics/rio-1.jpg', 7);
INSERT INTO poolhub.poolstore_poolhouseimage (id, image, poolhouse_id) VALUES (20, 'poolhall-pics/metropool-1.jpg', 8);
INSERT INTO poolhub.poolstore_poolhouseimage (id, image, poolhouse_id) VALUES (21, 'poolhall-pics/metropool-2.jpg', 8);
INSERT INTO poolhub.poolstore_poolhouseimage (id, image, poolhouse_id) VALUES (22, 'poolhall-pics/metropool-3.jpg', 8);
INSERT INTO poolhub.poolstore_poolhouseimage (id, image, poolhouse_id) VALUES (23, 'poolhall-pics/metropool-4.jpg', 8);
INSERT INTO poolhub.poolstore_poolhouseimage (id, image, poolhouse_id) VALUES (24, 'poolhall-pics/universe-3.jpeg', 9);
INSERT INTO poolhub.poolstore_poolhouseimage (id, image, poolhouse_id) VALUES (25, 'poolhall-pics/uni4verse-1.jpg', 9);
INSERT INTO poolhub.poolstore_poolhouseimage (id, image, poolhouse_id) VALUES (26, 'poolhall-pics/universe-2.jpg', 9);
INSERT INTO poolhub.poolstore_poolhouseimage (id, image, poolhouse_id) VALUES (27, 'poolhall-pics/te-1.jpg', 10);
INSERT INTO poolhub.poolstore_poolhouseimage (id, image, poolhouse_id) VALUES (28, 'poolhall-pics/te-2.jpg', 10);
INSERT INTO poolhub.poolstore_poolhouseimage (id, image, poolhouse_id) VALUES (29, 'poolhall-pics/te-3.jpg', 10);
INSERT INTO poolhub.poolstore_history (id, result_winner, result_loser, points_given, penalty_points, tie, timestamp, loser_player_id, winner_player_id, poolhouse_id) VALUES (1, 5, 3, 10, 2, 0, '2024-10-25 18:22:25.193216', 11, 32, 7);
INSERT INTO poolhub.poolstore_history (id, result_winner, result_loser, points_given, penalty_points, tie, timestamp, loser_player_id, winner_player_id, poolhouse_id) VALUES (3, 2, 1, 10, 2, 0, '2024-10-25 18:51:10.985987', 32, 11, 7);
INSERT INTO poolhub.poolstore_history (id, result_winner, result_loser, points_given, penalty_points, tie, timestamp, loser_player_id, winner_player_id, poolhouse_id) VALUES (4, 3, 1, 10, 2, 0, '2024-10-25 18:58:20.072209', 11, 32, 7);
