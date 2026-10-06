-- Migration for existing databases (create_all does not alter existing tables).
-- Run once against your Postgres DB.

ALTER TABLE "user" ADD CONSTRAINT uq_user_id_name UNIQUE (id, name);

ALTER TABLE staff ADD COLUMN IF NOT EXISTS name VARCHAR;
UPDATE staff s SET name = u.name FROM "user" u WHERE u.id = s.user_id;
ALTER TABLE staff ALTER COLUMN name SET NOT NULL;
ALTER TABLE staff DROP CONSTRAINT IF EXISTS staff_user_id_fkey;
ALTER TABLE staff ADD CONSTRAINT staff_user_id_name_fkey FOREIGN KEY (user_id, name)
    REFERENCES "user" (id, name) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE admin ADD COLUMN IF NOT EXISTS name VARCHAR;
UPDATE admin a SET name = u.name FROM "user" u WHERE u.id = a.user_id;
ALTER TABLE admin ALTER COLUMN name SET NOT NULL;
ALTER TABLE admin DROP CONSTRAINT IF EXISTS admin_user_id_fkey;
ALTER TABLE admin ADD CONSTRAINT admin_user_id_name_fkey FOREIGN KEY (user_id, name)
    REFERENCES "user" (id, name) ON UPDATE CASCADE ON DELETE CASCADE;
