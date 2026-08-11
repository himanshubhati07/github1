package com.example.app.repository;

import com.example.app.entity.Attendance;
import com.example.app.entity.Attendance.AttendanceStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface AttendanceRepository extends JpaRepository<Attendance, UUID> {

    Optional<Attendance> findByEmployeeIdAndAttendanceDate(String employeeId, LocalDate date);

    boolean existsByEmployeeIdAndAttendanceDate(String employeeId, LocalDate date);

    List<Attendance> findByEmployeeIdAndAttendanceDateBetween(String employeeId, LocalDate start, LocalDate end);

    List<Attendance> findByAttendanceDate(LocalDate date);

    long countByAttendanceDateAndStatus(LocalDate date, AttendanceStatus status);

    long countByAttendanceDateAndTimeOutIsNull(LocalDate date);

    @Query(value = "SELECT a.* FROM attendance a WHERE " +
           "(:employeeId IS NULL OR a.employee_id = CAST(:employeeId AS text)) " +
           "AND (:startDate IS NULL OR a.attendance_date >= CAST(:startDate AS date)) " +
           "AND (:endDate IS NULL OR a.attendance_date <= CAST(:endDate AS date)) " +
           "AND (:status IS NULL OR a.status = CAST(:status AS text)) " +
           "AND (:department IS NULL OR EXISTS (" +
           "  SELECT 1 FROM employees e WHERE e.employee_id = a.employee_id AND e.department = CAST(:department AS text))) " +
           "AND (:search IS NULL OR EXISTS (" +
           "  SELECT 1 FROM employees e WHERE e.employee_id = a.employee_id AND " +
           "  (LOWER(e.name) LIKE LOWER(CONCAT('%', CAST(:search AS text), '%')) " +
           "   OR LOWER(e.employee_id) LIKE LOWER(CONCAT('%', CAST(:search AS text), '%')))))",
           countQuery = "SELECT COUNT(*) FROM attendance a WHERE " +
           "(:employeeId IS NULL OR a.employee_id = CAST(:employeeId AS text)) " +
           "AND (:startDate IS NULL OR a.attendance_date >= CAST(:startDate AS date)) " +
           "AND (:endDate IS NULL OR a.attendance_date <= CAST(:endDate AS date)) " +
           "AND (:status IS NULL OR a.status = CAST(:status AS text)) " +
           "AND (:department IS NULL OR EXISTS (" +
           "  SELECT 1 FROM employees e WHERE e.employee_id = a.employee_id AND e.department = CAST(:department AS text))) " +
           "AND (:search IS NULL OR EXISTS (" +
           "  SELECT 1 FROM employees e WHERE e.employee_id = a.employee_id AND " +
           "  (LOWER(e.name) LIKE LOWER(CONCAT('%', CAST(:search AS text), '%')) " +
           "   OR LOWER(e.employee_id) LIKE LOWER(CONCAT('%', CAST(:search AS text), '%')))))",
           nativeQuery = true)
    Page<Attendance> filterAttendance(
            @Param("employeeId") String employeeId,
            @Param("startDate") LocalDate startDate,
            @Param("endDate") LocalDate endDate,
            @Param("status") String status,
            @Param("department") String department,
            @Param("search") String search,
            Pageable pageable);

    @Query("SELECT COUNT(a) FROM Attendance a WHERE a.attendanceDate = :date AND a.timeOut IS NULL AND a.timeIn IS NOT NULL")
    long countCheckedInOnDate(@Param("date") LocalDate date);
}
