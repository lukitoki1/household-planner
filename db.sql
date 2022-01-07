ALTER TABLE users ADD CONSTRAINT ix_user_name_unique UNIQUE (user_email);
ALTER TABLE users ADD COLUMN user_notification_email TEXT;