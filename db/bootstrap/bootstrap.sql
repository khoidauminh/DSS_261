
-- Reset the database
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- ====================================================================
-- PostgreSQL Star Schema for UCI Student Dropout Dataset
-- ====================================================================

-- Helper tables for table 1
CREATE TABLE Marital_Status(
    Marital_status_ID SERIAL PRIMARY KEY,
    Marital_status VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE Nationality(
    Nationality_ID SERIAL PRIMARY KEY,
    Nationality VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE Gender(
    Gender_ID SERIAL PRIMARY KEY,
    Gender VARCHAR(50) UNIQUE NOT NULL
);

-- 1. Dimension: Demographics
CREATE TABLE Dim_Demographics (
    Demographics_ID SERIAL PRIMARY KEY,
    Marital_status_ID INT REFERENCES Marital_Status(Marital_Status_ID),
    Nationality_ID INT REFERENCES Nationality(Nationality_ID),
    Displaced BOOLEAN,
    Gender_ID INT REFERENCES Gender(Gender_ID),
    Age_at_enrollment INT
);

-- Helper tables for table 2
CREATE TABLE Parent_Occupation(
    Parent_occupation_ID SERIAL PRIMARY KEY,
    Occupation VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE Parent_Qualification(
    Parent_qualification_ID SERIAL PRIMARY KEY,
    Qualification VARCHAR(255) UNIQUE NOT NULL
);

-- 2. Dimension: Socioeconomic Status
CREATE TABLE Dim_Socioeconomic (
    Socioeconomic_ID SERIAL PRIMARY KEY,
    Mother_qualification_ID INT REFERENCES Parent_Qualification(Parent_qualification_ID),
    Father_qualification_ID INT REFERENCES Parent_Qualification(Parent_qualification_ID),
    Mother_occupation_ID INT REFERENCES Parent_Occupation(Parent_occupation_ID),
    Father_occupation_ID INT REFERENCES Parent_Occupation(Parent_occupation_ID),
    Debtor BOOLEAN,
    Tuition_fees_up_to_date BOOLEAN,
    Scholarship_holder BOOLEAN
);

-- Helper tables for table 3
CREATE TABLE Course(
    Course_ID SERIAL PRIMARY KEY,
    Course VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE Application_Mode(
    Application_mode_ID SERIAL PRIMARY KEY,
    Application_Mode VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE Previous_Qualification(
    Previous_qualification_ID SERIAL PRIMARY KEY,
    Previous_qualification VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE Daytime_Evening_Attendance(
    Daytime_evening_attendance_ID SERIAL PRIMARY KEY,
    Daytime_evening_attendance VARCHAR(50) UNIQUE NOT NULL
);

-- 3. Dimension: Academic Course
CREATE TABLE Dim_Academic_Course (
    Academic_Course_ID SERIAL PRIMARY KEY,
    Course_ID INT REFERENCES Course(Course_ID),
    Application_mode_ID INT REFERENCES Application_Mode(Application_mode_ID),
    Application_order INT,
    Previous_qualification_ID INT REFERENCES Previous_Qualification(Previous_qualification_ID),
    Daytime_evening_attendance_ID INT REFERENCES Daytime_evening_attendance(Daytime_evening_attendance_ID)
);

-- 4. Dimension: Macroeconomic Factors
CREATE TABLE Dim_Macroeconomic (
    Macroeconomic_ID SERIAL PRIMARY KEY,
    Unemployment_rate NUMERIC(5,2),
    Inflation_rate NUMERIC(5,2),
    GDP NUMERIC(5,2)
);

-- Helper tables for table 5
-- [Dropout, Enrolled, Graduate]
CREATE TABLE Target_Outcome(
    Target_Outcome_ID SERIAL PRIMARY KEY,
    Target_Outcome VARCHAR(50) UNIQUE NOT NULL
);

-- 5. Fact Table: Academic Record
-- Grain: One row per student's overall record (suitable for the classification target)
CREATE TABLE Fact_Academic_Record (
    Student_ID SERIAL PRIMARY KEY, 
    Demographics_ID INT REFERENCES Dim_Demographics(Demographics_ID),
    Socioeconomic_ID INT REFERENCES Dim_Socioeconomic(Socioeconomic_ID),
    Academic_Course_ID INT REFERENCES Dim_Academic_Course(Academic_Course_ID),
    Macroeconomic_ID INT REFERENCES Dim_Macroeconomic(Macroeconomic_ID),
    
    -- 1st Semester Metrics
    CU_1st_sem_credited INT,
    CU_1st_sem_enrolled INT,
    CU_1st_sem_evaluations INT,
    CU_1st_sem_approved INT,
    CU_1st_sem_grade NUMERIC(5,2),
    CU_1st_sem_without_evaluations INT,
    
    -- 2nd Semester Metrics
    CU_2nd_sem_credited INT,
    CU_2nd_sem_enrolled INT,
    CU_2nd_sem_evaluations INT,
    CU_2nd_sem_approved INT,
    CU_2nd_sem_grade NUMERIC(5,2),
    CU_2nd_sem_without_evaluations INT,
    
    Target_Outcome_ID INT REFERENCES Target_Outcome(Target_Outcome_ID)
);

-- Indexes to optimize OLAP and DSS aggregation queries
CREATE INDEX idx_fact_demo ON Fact_Academic_Record(Demographics_ID);
CREATE INDEX idx_fact_socio ON Fact_Academic_Record(Socioeconomic_ID);
CREATE INDEX idx_fact_course ON Fact_Academic_Record(Academic_Course_ID);
CREATE INDEX idx_fact_macro ON Fact_Academic_Record(Macroeconomic_ID);
