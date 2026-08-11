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
import java.time.LocalTime;
import java.util.UUID;

@Entity
@Table(name = "attendance",
       uniqueConstraints = @UniqueConstraint(columnNames = {"employeeId", "attendanceDate"}))
@EntityListeners(AuditingEntityListener.class)
@Getter @Setter @NoArgsConstructor
public class Attendance {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false)
    private String employeeId;

    @Column(nullable = false)
    private LocalDate attendanceDate;

    private LocalTime timeIn;

    private LocalTime timeOut;

    /** Total working hours as decimal (e.g. 8.5 = 8h 30m) */
    private Double workingHours;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private AttendanceStatus status = AttendanceStatus.ABSENT;

    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(nullable = false)
    private LocalDateTime updatedAt;

    public enum AttendanceStatus { PRESENT, ABSENT, LATE }
}
