package com.example.app.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "employees",
       uniqueConstraints = {
           @UniqueConstraint(columnNames = "employeeId"),
           @UniqueConstraint(columnNames = "email")
       })
@EntityListeners(AuditingEntityListener.class)
@Getter @Setter @NoArgsConstructor
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false, unique = true)
    private String employeeId;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    private String phone;

    private String department;

    private String designation;

    private LocalDate joiningDate;

    private String photo;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private EmpStatus status = EmpStatus.ACTIVE;

    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(nullable = false)
    private LocalDateTime updatedAt;

    public enum EmpStatus { ACTIVE, INACTIVE }
}
