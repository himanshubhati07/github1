package com.example.app.repository;

import com.example.app.entity.FaceRegistration;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface FaceRegistrationRepository extends JpaRepository<FaceRegistration, UUID> {
    Optional<FaceRegistration> findByEmployeeId(String employeeId);
    boolean existsByEmployeeId(String employeeId);
}
