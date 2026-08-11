package com.example.app.repository;

import com.example.app.entity.Employee;
import com.example.app.entity.Employee.EmpStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface EmployeeRepository extends JpaRepository<Employee, UUID> {

    Optional<Employee> findByEmployeeId(String employeeId);

    boolean existsByEmployeeId(String employeeId);

    boolean existsByEmail(String email);

    long countByStatus(EmpStatus status);

    @Query(value = "SELECT * FROM employees e WHERE " +
           "(:search IS NULL OR LOWER(e.name) LIKE LOWER(CONCAT('%', CAST(:search AS text), '%')) " +
           "  OR LOWER(e.employee_id) LIKE LOWER(CONCAT('%', CAST(:search AS text), '%')) " +
           "  OR LOWER(e.email) LIKE LOWER(CONCAT('%', CAST(:search AS text), '%'))) " +
           "AND (:department IS NULL OR e.department = CAST(:department AS text)) " +
           "AND (:status IS NULL OR e.status = CAST(:status AS text))",
           countQuery = "SELECT COUNT(*) FROM employees e WHERE " +
           "(:search IS NULL OR LOWER(e.name) LIKE LOWER(CONCAT('%', CAST(:search AS text), '%')) " +
           "  OR LOWER(e.employee_id) LIKE LOWER(CONCAT('%', CAST(:search AS text), '%')) " +
           "  OR LOWER(e.email) LIKE LOWER(CONCAT('%', CAST(:search AS text), '%'))) " +
           "AND (:department IS NULL OR e.department = CAST(:department AS text)) " +
           "AND (:status IS NULL OR e.status = CAST(:status AS text))",
           nativeQuery = true)
    Page<Employee> searchEmployees(
            @Param("search") String search,
            @Param("department") String department,
            @Param("status") String status,
            Pageable pageable);
}
