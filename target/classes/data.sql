-- Departments
INSERT INTO departments (id, name, status, created_at, updated_at)
VALUES
  ('a1b2c3d4-0001-0001-0001-000000000001', 'Engineering', 'ACTIVE', NOW(), NOW()),
  ('a1b2c3d4-0001-0001-0001-000000000002', 'Human Resources', 'ACTIVE', NOW(), NOW()),
  ('a1b2c3d4-0001-0001-0001-000000000003', 'Sales', 'ACTIVE', NOW(), NOW()),
  ('a1b2c3d4-0001-0001-0001-000000000004', 'Finance', 'ACTIVE', NOW(), NOW()),
  ('a1b2c3d4-0001-0001-0001-000000000005', 'Operations', 'ACTIVE', NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- Admin user (password: Admin@123)
INSERT INTO users (id, name, email, password, role, status, created_at, updated_at)
VALUES
  ('b1b2c3d4-0001-0001-0001-000000000001', 'System Admin', 'admin@company.com',
   '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', 'ADMIN', 'ACTIVE', NOW(), NOW()),
  ('b1b2c3d4-0001-0001-0001-000000000002', 'HR Manager', 'hr@company.com',
   '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5EH', 'HR', 'ACTIVE', NOW(), NOW())
ON CONFLICT (email) DO NOTHING;

-- Employees
INSERT INTO employees (id, employee_id, name, email, phone, department, designation, joining_date, status, created_at, updated_at)
VALUES
  ('c1b2c3d4-0001-0001-0001-000000000001', 'EMP001', 'Rahul Sharma', 'rahul.sharma@company.com', '9876543210', 'Engineering', 'Senior Developer', '2022-01-15', 'ACTIVE', NOW(), NOW()),
  ('c1b2c3d4-0001-0001-0001-000000000002', 'EMP002', 'Priya Patel', 'priya.patel@company.com', '9876543211', 'Human Resources', 'HR Executive', '2022-03-01', 'ACTIVE', NOW(), NOW()),
  ('c1b2c3d4-0001-0001-0001-000000000003', 'EMP003', 'Amit Kumar', 'amit.kumar@company.com', '9876543212', 'Sales', 'Sales Manager', '2021-07-20', 'ACTIVE', NOW(), NOW()),
  ('c1b2c3d4-0001-0001-0001-000000000004', 'EMP004', 'Sneha Gupta', 'sneha.gupta@company.com', '9876543213', 'Finance', 'Accountant', '2023-02-10', 'ACTIVE', NOW(), NOW()),
  ('c1b2c3d4-0001-0001-0001-000000000005', 'EMP005', 'Vijay Singh', 'vijay.singh@company.com', '9876543214', 'Engineering', 'Junior Developer', '2023-06-01', 'ACTIVE', NOW(), NOW())
ON CONFLICT (employee_id) DO NOTHING;

-- Face registrations (demo face data)
INSERT INTO face_registrations (id, employee_id, face_reference, registered_at, updated_at)
VALUES
  ('d1b2c3d4-0001-0001-0001-000000000001', 'EMP001', 'FACE_DEMO_EMP001', NOW(), NOW()),
  ('d1b2c3d4-0001-0001-0001-000000000002', 'EMP002', 'FACE_DEMO_EMP002', NOW(), NOW()),
  ('d1b2c3d4-0001-0001-0001-000000000003', 'EMP003', 'FACE_DEMO_EMP003', NOW(), NOW())
ON CONFLICT (employee_id) DO NOTHING;

-- Attendance records for today and yesterday
INSERT INTO attendance (id, employee_id, attendance_date, time_in, time_out, working_hours, status, created_at, updated_at)
VALUES
  ('e1b2c3d4-0001-0001-0001-000000000001', 'EMP001', CURRENT_DATE - INTERVAL '1 day', '09:00:00', '18:00:00', 9.0, 'PRESENT', NOW(), NOW()),
  ('e1b2c3d4-0001-0001-0001-000000000002', 'EMP002', CURRENT_DATE - INTERVAL '1 day', '09:15:00', '17:30:00', 8.25, 'PRESENT', NOW(), NOW()),
  ('e1b2c3d4-0001-0001-0001-000000000003', 'EMP003', CURRENT_DATE - INTERVAL '1 day', '09:30:00', '18:30:00', 9.0, 'LATE', NOW(), NOW()),
  ('e1b2c3d4-0001-0001-0001-000000000004', 'EMP004', CURRENT_DATE - INTERVAL '1 day', '08:45:00', '17:45:00', 9.0, 'PRESENT', NOW(), NOW()),
  ('e1b2c3d4-0001-0001-0001-000000000005', 'EMP005', CURRENT_DATE - INTERVAL '2 days', '09:00:00', '18:00:00', 9.0, 'PRESENT', NOW(), NOW()),
  ('e1b2c3d4-0001-0001-0001-000000000006', 'EMP001', CURRENT_DATE - INTERVAL '2 days', '09:05:00', '18:10:00', 9.08, 'PRESENT', NOW(), NOW())
ON CONFLICT (employee_id, attendance_date) DO NOTHING;
