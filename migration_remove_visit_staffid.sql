-- Migration script to remove StaffId from Visit table
-- This aligns the database schema with our new VisitStaff association table structure

-- Step 1: Remove the StaffId foreign key constraint first
ALTER TABLE `Visit` DROP FOREIGN KEY IF EXISTS `Visit_ibfk_3`;

-- Step 2: Remove the StaffId index
ALTER TABLE `Visit` DROP INDEX IF EXISTS `StaffId`;

-- Step 3: Remove the StaffId column
ALTER TABLE `Visit` DROP COLUMN `StaffId`;

-- Step 4: Verify the new structure
-- The Visit table should now only have:
-- - VisitId (primary key)
-- - PatientId (foreign key to Patient)
-- - VisitPurpose (enum)
-- - VisitTime (datetime)

-- Note: Staff relationships are now handled through the VisitStaff table
-- which creates a many-to-many relationship between Visit and Staff
