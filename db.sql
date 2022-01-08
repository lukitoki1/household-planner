ALTER TABLE users ADD CONSTRAINT ix_user_name_unique UNIQUE (user_email);
ALTER TABLE users ADD COLUMN user_notification_email TEXT;
ALTER TABLE users DROP COLUMN user_phone_number;

ALTER TABLE users DROP COLUMN user_notification_email;

ALTER TABLE  household_members ADD CONSTRAINT ix_hous_user_id_unique UNIQUE (hsme_hous_id, hsme_user_id);

ALTER TABLE chores ALTER chor_start_date TYPE timestamptz USING chor_start_date AT TIME ZONE 'UTC';